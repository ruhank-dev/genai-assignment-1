# Task 4 test metrics

| split | n | L1 | SSIM | PSNR | LPIPS |
|---|---|---|---|---|---|
| overall | 1046 | 0.1001 | 0.4983 | 16.14 | 0.3818 |
| style1 | 619 | 0.0750 | 0.5455 | 17.90 | 0.4060 |
| style2 | 381 | 0.1456 | 0.4057 | 12.90 | 0.3540 |
| style3 | 46 | 0.0614 | 0.6301 | 19.20 | 0.2859 |

FID (overall): 102.06

FID uses 1046 images for a 2048-d feature covariance (rank-deficient): treat as a relative number; per-style FID is not reported because style 2/3 have only 381/46 test images.