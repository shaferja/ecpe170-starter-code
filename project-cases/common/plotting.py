"""Baseline plots with explicit timing scopes and evidence provenance."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def read_rows(path):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f'{path}: no data rows')
    if any(r.get('correct', 'PASS') != 'PASS' for r in rows):
        raise ValueError(f'{path}: correctness failed; resolve before plotting performance')
    return rows


def number(row, key):
    value = float(row[key])
    if not math.isfinite(value) or value < 0:
        raise ValueError(f'{key} must be finite and nonnegative')
    return value


def unique(rows, keys):
    values = [tuple(r[k] for k in keys) for r in rows]
    if len(values) != len(set(values)):
        raise ValueError('Repeated workload rows: use a CSV from one baseline session')


def constant(rows, keys):
    for key in keys:
        if len({r[key] for r in rows}) != 1:
            raise ValueError(f'Mixed {key}: plot one controlled baseline session at a time')


def make_figure(case, rows, trace, source):
    import matplotlib.pyplot as plt
    if case == 'A':
        unique(rows, ['clients'])
        constant(rows, ['architecture', 'python_version', 'host', 'port', 'database_size', 'dimension', 'seed', 'timed_scope'])
        rows = sorted(rows, key=lambda r: number(r, 'clients'))
        x = list(range(len(rows)))
        fig, axes = plt.subplots(1, 2, figsize=(12, 6), layout='constrained')
        for key, label in [('p50_latency_ms', 'p50'), ('p95_latency_ms', 'p95')]:
            axes[0].plot(x, [number(r, key) if number(r, 'success_count') else math.nan for r in rows], 'o-', label=label)
        axes[0].set(ylabel='Successful-request latency (ms)', title='Client response time')
        axes[0].legend()
        axes[1].bar(x, [number(r, 'throughput_rps') for r in rows], color='#15847b')
        axes[1].set(ylabel='Successful requests / second', title='Completed work and errors')
        for i, r in enumerate(rows):
            requests = number(r, 'request_count')
            success, errors = number(r, 'success_count'), number(r, 'error_count')
            if requests != success + errors:
                raise ValueError('Request counts do not reconcile')
            axes[1].annotate(f'{int(errors)}/{int(requests)} errors', (i, number(r, 'throughput_rps')), xytext=(0, 6), textcoords='offset points', ha='center')
        axes[1].margins(y=.25)
        for ax in axes:
            ax.set_xticks(x, [r['clients'] for r in rows]); ax.set_xlabel('Concurrent clients')
        note='One run per load; successful-request percentiles are not uncertainty intervals.\nClient scope: connect, send, queue, compute, response, receive and validate; startup excluded.'
    elif case == 'B':
        unique(rows, ['vector_count', 'scope'])
        constant(rows, ['architecture', 'python_version', 'dimension', 'query_count', 'trials', 'warmups'])
        scopes = ['python', 'native_conversion_inclusive', 'native_reused_index']
        labels = ['Python search', 'Native: conversion included', 'Native: reused index and queries']
        sizes = sorted({int(r['vector_count']) for r in rows})
        fig, axes = plt.subplots(1, 2, figsize=(12, 6), layout='constrained')
        for scope, label in zip(scopes, labels):
            series=[]; ratios=[]
            for size in sizes:
                group=[r for r in rows if int(r['vector_count']) == size]
                constant(group, ['seed'])
                if {r['scope'] for r in group} != set(scopes):
                    raise ValueError('Each workload must contain all three timing scopes')
                value=number(next(r for r in group if r['scope']==scope), 'median_ms_per_query')
                baseline=number(next(r for r in group if r['scope']=='python'), 'median_ms_per_query')
                if value <= 0 or baseline <= 0: raise ValueError('Timing must be positive')
                series.append(value); ratios.append(baseline/value)
            axes[0].plot(sizes, series, 'o-', label=label)
            axes[1].plot(sizes, ratios, 'o-', label=label)
        axes[0].set(yscale='log', ylabel='Median milliseconds / query (log scale)', title='Measured timing scopes')
        axes[1].set(ylabel='Python median / plotted-scope median', title='Speed relative to Python')
        axes[1].axhline(1, color='gray', linestyle='--')
        for ax in axes:
            ax.set_xscale('log'); ax.set_xlabel('Database vectors (log scale)'); ax.legend(fontsize=8)
        note='Medians over trials; no variability inferred from summary rows. Data generation excluded.\nReused scope excludes index/query conversion; native calls and result return are included. Ratios compare different scopes.'
    else:
        unique(rows, ['batch_size'])
        constant(rows, ['provenance', 'architecture', 'python_version', 'vectors', 'dimension', 'trials', 'warmups', 'seed', 'timed_scope'])
        unique(trace, ['residency', 'batch_size'])
        fig, axes = plt.subplots(1, 3, figsize=(15, 6), layout='constrained')
        rows=sorted(rows, key=lambda r:number(r, 'batch_size'))
        axes[0].plot([number(r,'batch_size') for r in rows], [number(r,'median_cpu_total_ms') for r in rows], 'o-', label='VM CPU batch total')
        axes[0].set(title='Your VM: CPU measurements', ylabel='Median batch time (ms)')
        for ax, residency in zip(axes[1:], ['database-resident', 'copy-each-request']):
            group=sorted([r for r in trace if r['residency']==residency], key=lambda r:number(r,'batch_size'))
            if not group: raise ValueError(f'Missing trace residency: {residency}')
            for r in group:
                if not math.isclose(sum(number(r,k) for k in ['h2d_ms','compute_ms','d2h_ms']),number(r,'gpu_total_ms'),abs_tol=1e-9):
                    raise ValueError('Trace component total mismatch')
            for key,label in [('cpu_total_ms','Trace CPU total'),('gpu_total_ms','Trace GPU total'),('compute_ms','GPU launch/compute')]:
                ax.plot([number(r,'batch_size') for r in group], [number(r,key) for r in group], 'o-', label=label)
            ax.set(title=f'Teaching trace: {residency}', ylabel='Batch time (ms)')
        for ax in axes:
            ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('Queries per batch (log scale)'); ax.set_ylabel('Batch time (ms, log scale)'); ax.legend(fontsize=8)
        note='Left: measured on your VM; CPU data generation excluded. Right: instructor-provided teaching trace.\nPanels use separate y scales. Compare CPU/GPU only within the trace; never form a VM-to-trace speedup.'
    for ax in axes:
        ax.grid(alpha=.2); ax.spines[['top','right']].set_visible(False)
    fig.suptitle(f'Case {case}: baseline evidence — {source}', fontsize=16)
    fig.supxlabel(note, fontsize=9)
    return fig


def main(case):
    parser=argparse.ArgumentParser(description=f'Plot Case {case} baseline CSV evidence.')
    parser.add_argument('csv', type=Path)
    if case=='C': parser.add_argument('--trace', type=Path, default=Path('gpu_trace_packet.csv'))
    parser.add_argument('--save', type=Path)
    parser.add_argument('--no-show', action='store_true')
    args=parser.parse_args()
    if args.no_show and not args.save: parser.error('--no-show requires --save')
    if args.save and args.save.suffix.lower()!='.png': parser.error('--save must name a .png file')
    try:
        import matplotlib
        if args.no_show: matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        rows=read_rows(args.csv)
        trace=read_rows(args.trace) if case=='C' else None
        fig=make_figure(case, rows, trace, args.csv.name)
    except ImportError:
        parser.error('Install Matplotlib in your project environment: python -m pip install matplotlib')
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
        parser.error(f'Invalid baseline CSV: {error}')
    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.save,dpi=160); print(f'Saved graph: {args.save}')
    if not args.no_show: plt.show()
    plt.close(fig)
