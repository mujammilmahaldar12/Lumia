import torch

print('='*60)
print('GPU STATUS CHECK')
print('='*60)
print(f'PyTorch Version: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'GPU Name: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
    print(f'CUDA Version: {torch.version.cuda}')
    print('✅ GPU READY FOR LUMIA!')
else:
    print('❌ GPU NOT DETECTED')
    print('Make sure you activated virtual environment:')
    print('  cd "c:\\Users\\mujammil maldar\\Desktop\\New folder (4)\\app"')
    print('  .\\env\\Scripts\\activate')

print('='*60)
