#!/bin/bash
echo_status() { local msg=$1; echo "[$(date -u +%Y-%m-%dT%H:%M:%S%Z)] $msg" | tee -a ~/status; }

echo_status "on-create start"
pip install --no-cache-dir ipython ipykernel
pip install "black[jupyter]"
pip install isort

# only run apt upgrade on pre-build
sudo apt-get update
if [ "$CODESPACE_NAME" = "null" ]
then
    echo_status "apt upgrading"
    sudo apt-get upgrade -y
fi

###############################
## Additional git and zsh setup
###############################
echo_status "  setting up some git and zsh goodies"
# setup easy git aliases and git-delta for git-diff
cp .devcontainer/gitconfig-base ~/.gitconfig
wget -q  "$(curl -s https://api.github.com/repos/dandavison/delta/releases/latest | jq '.assets[].browser_download_url' -r | grep -vE 'musl|darwin|arm|apple|windows' | grep 'amd64.*deb')" -O /tmp/delta.deb
sudo dpkg -i /tmp/delta.deb
# ZSH
echo "autoload -U select-word-style
select-word-style bash
zstyle ':completion:*:*:docker:*' option-stacking yes
zstyle ':completion:*:*:docker-*:*' option-stacking yes
bindkey '^U' backward-kill-line
bindkey '^Y' yank" >> ~/.zshrc
###############################

# permanently change shell to zsh for codespace user
sudo chsh --shell /bin/zsh "$USER"
echo_status "on-create complete"
