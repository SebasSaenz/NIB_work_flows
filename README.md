# Bioinformatic workflows use in NIB

Time-series study of the Lake Bled phageome.

git clone --filter=blob:none --no-checkout https://github.com/OWNER/REPO.git
cd REPO

git sparse-checkout init --no-cone
git sparse-checkout set --no-cone \
    '/scripts/' \
    '/config/' \
    '/README.md' \
    '/analysis/pipeline.py'

git checkout
