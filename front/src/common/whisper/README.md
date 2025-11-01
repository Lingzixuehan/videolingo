运行main.py所需依赖

whisper官方网址：https://github.com/openai/whisper
conda官方网址：https://anaconda.org/anaconda/conda
cuda官方网址：https://developer.nvidia.com/cuda-toolkit
pytorch官方网址：https://pytorch.org/

安装conda

安装对应显卡版本的cuda
命令行输入nvidia-smi.exe查看当前驱动支持的最高版本cuda
最好不要超过12.4，这是conda安装pytorch支持的最高版本cuda

创建安装路径

将路径加入到 Conda 配置文件
conda config --add envs_dirs "path"
将"path"，改成你设置的安装路径

创建虚拟环境
conda create -n "whisper-env" python=3.11

激活环境
conda activate whisper-env

安装对应cuda版本的pytorch
添加清华镜像源：
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/menpo/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
安装pytorch:
conda install pytorch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 pytorch-cuda=12.4 -c nvidia
注意这里对应的cuda是12.4

安装ffmpeg
onda install ffmpeg -c conda-forge
pip install ffmpeg-python

安装whisper
国内安装：pip install -U openai-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple