set -e

DIST_DIR=dist
DIST_TAR=dist.tar
NIX_SH=/etc/profile.d/nix.sh

tar cvf $DIST_TAR $DIST_DIR

scp $DIST_TAR $SSH_ALIAS:proj/xtube

cat <<EOF | ssh $SSH_ALIAS 'bash -s'
set -e
[ -f $NIX_SH ] && . $NIX_SH
cd proj/xtube
git fetch
git reset --hard origin/main
rm -rf $DIST_DIR
tar xf $DIST_TAR
rm $DIST_TAR
yarn build-docker
cd ../web
docker compose up -d xtube
EOF
