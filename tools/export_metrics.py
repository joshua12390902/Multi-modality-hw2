#!/usr/bin/env python3
"""
Export evaluation metrics to CSV and summary JSON
Reads medimodel_results.json and generates:
1. metrics_summary.csv - All metrics for all slices/qualities
2. metrics_average.json - Average performance summary
"""

import json
import csv
from pathlib import Path

def export_metrics():
    results_dir = Path('/workspace/MMIP_hw2/results_real')
    input_json = results_dir / 'medimodel_results.json'
    output_csv = results_dir / 'metrics_summary.csv'
    output_summary_json = results_dir / 'metrics_average.json'
    
    # Read results
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV data
    csv_rows = []
    header = [
        'Slice', 'Quality', 'Compressed_Bytes', 'Bits_Per_Pixel', 
        'Compression_Ratio', 'RMSE', 'PSNR_dB', 'SSIM', 'Edge_RMSE', 'Edge_PSNR_dB'
    ]
    
    for result in data['results']:
        slice_name = result['slice']
        for quality_str, metrics in result['qualities'].items():
            row = [
                slice_name,
                quality_str,
                metrics['compressed_bytes'],
                f"{metrics['bits_per_pixel']:.4f}",
                f"{metrics['compression_ratio']:.2f}",
                f"{metrics['rmse']:.2f}",
                f"{metrics['psnr_db']:.2f}",
                f"{metrics['ssim']:.4f}",
                f"{metrics['edge_rmse']:.2f}",
                f"{metrics['edge_psnr_db']:.2f}"
            ]
            csv_rows.append(row)
    
    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(csv_rows)
    
    print(f"✓ CSV exported: {output_csv}")
    print(f"  Rows: {len(csv_rows)} (header + {len(csv_rows)} data rows)")
    
    # Calculate averages per quality
    qualities = [30, 60, 90]
    summary = {
        'dataset': data['dataset'],
        'source': data['source'],
        'slices_evaluated': data['slices_evaluated'],
        'quality_levels': qualities,
        'average_metrics': {}
    }
    
    for quality in qualities:
        q_str = str(quality)
        metrics_list = [r['qualities'][q_str] for r in data['results']]
        
        avg = {
            'compressed_bytes': sum(m['compressed_bytes'] for m in metrics_list) / len(metrics_list),
            'bits_per_pixel': sum(m['bits_per_pixel'] for m in metrics_list) / len(metrics_list),
            'compression_ratio': sum(m['compression_ratio'] for m in metrics_list) / len(metrics_list),
            'rmse': sum(m['rmse'] for m in metrics_list) / len(metrics_list),
            'psnr_db': sum(m['psnr_db'] for m in metrics_list) / len(metrics_list),
            'ssim': sum(m['ssim'] for m in metrics_list) / len(metrics_list),
            'edge_rmse': sum(m['edge_rmse'] for m in metrics_list) / len(metrics_list),
            'edge_psnr_db': sum(m['edge_psnr_db'] for m in metrics_list) / len(metrics_list)
        }
        
        summary['average_metrics'][q_str] = avg
    
    # Write summary JSON
    with open(output_summary_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Summary JSON exported: {output_summary_json}")
    
    # Print summary table
    print("\n" + "="*80)
    print("Average Performance Summary")
    print("="*80)
    print(f"{'Quality':<8} {'Size(B)':<10} {'bpp':<8} {'Ratio':<8} {'PSNR':<8} {'SSIM':<8} {'Edge PSNR':<10}")
    print("-"*80)
    
    for quality in qualities:
        q_str = str(quality)
        m = summary['average_metrics'][q_str]
        print(f"{quality:<8} {m['compressed_bytes']:<10.0f} {m['bits_per_pixel']:<8.3f} "
              f"{m['compression_ratio']:<8.2f} {m['psnr_db']:<8.2f} "
              f"{m['ssim']:<8.4f} {m['edge_psnr_db']:<10.2f}")
    
    print("="*80)

if __name__ == '__main__':
    export_metrics()
