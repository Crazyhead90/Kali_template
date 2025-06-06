#!/bin/bash

apt install -y python3 python3-pip python3-venv seclists

mkdir -p $HOME/httpserver/shells
mkdir -p $HOME/httpserver/enum
mkdir -p $HOME/httpserver/privesc
mkdir -p $HOME/ligolo-ng/

cp /usr/share/peass/winpeas/winPEASx64.exe $HOME/httpserver/enum/
cp /usr/share/peass/winpeas/winPEASx86.exe $HOME/httpserver/enum/
cp /usr/share/peass/linpeas/linpeas.sh $HOME/httpserver/enum/

cp /usr/share/windows-resources/mimikatz/Win32/mimikatz.exe $HOME/httpserver/privesc/mimikatz32.exe
cp /usr/share/windows-resources/mimikatz/x64/mimikatz.exe $HOME/httpserver/privesc/mimikatz64.exe

cp /usr/share/windows-resources/binaries/nc.exe $HOME/httpserver/shells/
cp /usr/share/webshells/ $HOME/httpserver/shells/


# Install and configure Oh My Zsh
sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
git clone https://github.com/marlonrichert/zsh-autocomplete.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autocomplete
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
sed -i -e 's:plugins.*:plugins=(git zsh-autocomplete zsh-autosuggestions zsh-syntax-highlighting):g' $HOME/.zshrc


# Download and extract ligolo-ng agent
cd $HOME/ligolo-ng/
tar xvf =(curl -s https://api.github.com/repos/nicocha30/ligolo-ng/releases/latest | grep '"browser_download_url":' | grep 'agent_*_linux_amd64.tar.gz' | grep -vE '(\.pem|\.sig)' | grep -o 'https://[^"]*' | xargs wget | gunzip)
tar xvf =(curl -s https://api.github.com/repos/nicocha30/ligolo-ng/releases/latest | grep '"browser_download_url":' | grep 'proxy_*_linux_amd64.tar.gz' | grep -vE '(\.pem|\.sig)' | grep -o 'https://[^"]*' | xargs wget | gunzip)
unzip =(curl -s https://api.github.com/repos/nicocha30/ligolo-ng/releases/latest | grep '"browser_download_url":' | grep 'agent_*_windows_amd64.zip' | grep -vE '(\.pem|\.sig)' | grep -o 'https://[^"]*' | xargs wget -qO-)