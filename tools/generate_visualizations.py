#!/usr/bin/env python3
"""
生成評估結果視覺化圖表
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 從評估腳本重用 DICOM 讀取與編解碼流程
from evaluate_real_data import read_dicom_sitk, encode_image_direct, decode_image_direct

# 設定中文字體（優先使用 Noto CJK，缺字時再回退）
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = [
    'Noto Sans CJK TC', 'Noto Sans CJK SC', 'Noto Sans CJK JP',
    'Noto Sans', 'DejaVu Sans'
]
plt.rcParams['axes.unicode_minus'] = False

# 讀取結果
results_file = '/workspace/MMIP_hw2/results_real/medimodel_results.json'
with open(results_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取數據
qualities = [30, 60, 90]
psnr_values = {}
compression_values = {}
bpp_values = {}

for quality in qualities:
    psnr_list = []
    compression_list = []
    bpp_list = []
    
    for result in data['results']:
        q_data = result['qualities'][str(quality)]
        psnr_list.append(q_data['psnr_db'])
        compression_list.append(q_data['compression_ratio'])
        bpp_list.append(q_data['bits_per_pixel'])
    
    psnr_values[quality] = np.mean(psnr_list)
    compression_values[quality] = np.mean(compression_list)
    bpp_values[quality] = np.mean(bpp_list)

# 創建圖表
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# 1. PSNR vs Quality
ax = axes[0]
psnr_list = [psnr_values[q] for q in qualities]
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
bars1 = ax.bar(range(len(qualities)), psnr_list, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax.set_xticks(range(len(qualities)))
ax.set_xticklabels([f'Q={q}' for q in qualities], fontsize=14, fontweight='bold')
ax.set_ylabel('PSNR (dB)', fontsize=14, fontweight='bold')
ax.set_title('品質 vs PSNR\n(越高越好)', fontsize=15, fontweight='bold')
ax.grid(axis='y', alpha=0.3, linestyle='--')
for i, (bar, val) in enumerate(zip(bars1, psnr_list)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.2f} dB', ha='center', va='bottom', fontsize=12, fontweight='bold')

# 2. Compression Ratio vs Quality
ax = axes[1]
comp_list = [compression_values[q] for q in qualities]
bars2 = ax.bar(range(len(qualities)), comp_list, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax.set_xticks(range(len(qualities)))
ax.set_xticklabels([f'Q={q}' for q in qualities], fontsize=14, fontweight='bold')
ax.set_ylabel('壓縮率 (:1)', fontsize=14, fontweight='bold')
ax.set_title('品質 vs 壓縮率\n(越高越好)', fontsize=15, fontweight='bold')
ax.grid(axis='y', alpha=0.3, linestyle='--')
for i, (bar, val) in enumerate(zip(bars2, comp_list)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.2f}:1', ha='center', va='bottom', fontsize=12, fontweight='bold')

# 3. Bits per Pixel vs Quality
ax = axes[2]
bpp_list = [bpp_values[q] for q in qualities]
bars3 = ax.bar(range(len(qualities)), bpp_list, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax.set_xticks(range(len(qualities)))
ax.set_xticklabels([f'Q={q}' for q in qualities], fontsize=14, fontweight='bold')
ax.set_ylabel('比特率 (bpp)', fontsize=14, fontweight='bold')
ax.set_title('品質 vs 比特率\n(越低越好)', fontsize=15, fontweight='bold')
ax.grid(axis='y', alpha=0.3, linestyle='--')
for i, (bar, val) in enumerate(zip(bars3, bpp_list)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('/workspace/MMIP_hw2/results_real/performance_comparison.png', dpi=300, bbox_inches='tight')
print("✓ 已儲存: performance_comparison.png")

# Rate-Distortion 曲線
fig, ax = plt.subplots(figsize=(10, 6))

psnr_list = [psnr_values[q] for q in qualities]
compression_list = [compression_values[q] for q in qualities]

# 繪製曲線
ax.plot(compression_list, psnr_list, 'o-', linewidth=3, markersize=12, 
        color='#2E86AB', markerfacecolor='#A23B72', markeredgewidth=2, markeredgecolor='#2E86AB')

# 標記點
for comp, psnr, q in zip(compression_list, psnr_list, qualities):
    ax.annotate(f'Q={q}\n{psnr:.2f}dB\n{comp:.2f}:1', 
                xy=(comp, psnr), xytext=(0, 15), textcoords='offset points',
                ha='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

ax.set_xlabel('壓縮率 (Original / Compressed) (:1)', fontsize=14, fontweight='bold')
ax.set_ylabel('PSNR (dB)', fontsize=14, fontweight='bold')
ax.set_title('Rate-Distortion 曲線\n(Medimodel Human_Skull_2 CT)', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(14, 16)
ax.set_ylim(48, 62)

plt.tight_layout()
plt.savefig('/workspace/MMIP_hw2/results_real/rate_distortion_curve.png', dpi=300, bbox_inches='tight')
print("✓ 已儲存: rate_distortion_curve.png")

# 每片結果詳細圖
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

slices = ['I50', 'I100', 'I150', 'I200', 'I250']
for idx, (result, ax) in enumerate(zip(data['results'], axes[:5])):
    slice_name = result['slice'].replace('.dcm', '')
    qualities_data = result['qualities']
    
    qualities_list = [30, 60, 90]
    psnr_list = [qualities_data[str(q)]['psnr_db'] for q in qualities_list]
    
    bars = ax.bar(range(len(qualities_list)), psnr_list, 
                  color=['#FF6B6B', '#4ECDC4', '#45B7D1'], 
                  alpha=0.8, edgecolor='black', linewidth=2)
    
    ax.set_xticks(range(len(qualities_list)))
    ax.set_xticklabels([f'Q={q}' for q in qualities_list], fontweight='bold', fontsize=11)
    ax.set_ylabel('PSNR (dB)', fontweight='bold', fontsize=11)
    ax.set_title(f'{slice_name} - 值範圍 {result["value_range"][0]:.0f}~{result["value_range"][1]:.0f}', 
                 fontweight='bold', fontsize=12)
    ax.set_ylim(40, 70)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, val in zip(bars, psnr_list):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# 移除多餘的子圖
axes[5].remove()

plt.suptitle('各切片 PSNR 性能 (Medimodel Human_Skull_2 CT)', 
             fontsize=16, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('/workspace/MMIP_hw2/results_real/slice_details.png', dpi=300, bbox_inches='tight')
print("✓ 已儲存: slice_details.png")

# 生成定性重建與誤差圖
def generate_qualitative_example():
    dicom_dir = Path('/workspace/MMIP_hw2/2_skull_ct/DICOM_dcm')
    slice_name = 'I150.dcm'
    quality = 60
    output_path = Path('/workspace/MMIP_hw2/results_real/qualitative_I150_Q60.png')

    slice_path = dicom_dir / slice_name
    if not slice_path.exists():
        print(f"⚠ 找不到 DICOM: {slice_path}")
        return

    image = read_dicom_sitk(slice_path)
    if image is None:
        print("⚠ 無法讀取 DICOM")
        return

    bitstream = encode_image_direct(image, quality)
    recon = decode_image_direct(bitstream)

    # 視覺化時做簡單視窗化，避免灰階範圍過寬
    def window(img):
        vmin, vmax = np.percentile(img, [0.5, 99.5])
        return np.clip((img - vmin) / (vmax - vmin + 1e-6), 0, 1)

    orig_vis = window(image)
    recon_vis = window(recon)

    abs_err = np.abs(image - recon)
    err_max = max(np.quantile(abs_err, 0.995), 1e-6)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    im0 = axes[0].imshow(orig_vis, cmap='gray')
    axes[0].set_title('原始影像 (I150)', fontsize=14, fontweight='bold')
    axes[0].axis('off')

    im1 = axes[1].imshow(recon_vis, cmap='gray')
    axes[1].set_title('重建影像 (Q=60)', fontsize=14, fontweight='bold')
    axes[1].axis('off')

    im2 = axes[2].imshow(abs_err, cmap='magma', vmax=err_max)
    axes[2].set_title('誤差圖 (|原始-重建|)', fontsize=14, fontweight='bold')
    axes[2].axis('off')
    cbar = fig.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel('絕對差', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 已儲存: {output_path.name}")

generate_qualitative_example()

print("\n圖表已全部生成！")
print("  - performance_comparison.png")
print("  - rate_distortion_curve.png")
print("  - slice_details.png")
print("  - qualitative_I150_Q60.png")
