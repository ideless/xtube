set -e

SSH_PRIVATE_KEY_FILE=~/.ssh/$SSH_ALIAS.key

mkdir -p ~/.ssh/

echo "$SSH_PRIVATE_KEY" >$SSH_PRIVATE_KEY_FILE
chmod 600 $SSH_PRIVATE_KEY_FILE

ssh-keyscan -H $SSH_HOST >~/.ssh/known_hosts

cat <<EOF >~/.ssh/config
Host $SSH_ALIAS
  User $SSH_USER
  HostName $SSH_HOST
  IdentityFile $SSH_PRIVATE_KEY_FILE
EOF
