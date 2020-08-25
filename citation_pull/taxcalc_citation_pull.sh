#!/bin/bash

cd $HOME/Desktop/repos/Tax-Calculator
git fetch upstream
git merge upstream/master
export DATE=`date +%Y-%m-%d`
export BRANCH_NAME=citations-$DATE
git checkout -b $BRANCH_NAME

curl -H 'Zotero-API-Version: 2' -H 'Zotero-API-Key: MiQBsz0ilWhpsmQJyqeO2TzU' 'https://api.zotero.org/groups/2524233/items?format=bibtex' --output citations.bib

git status
git add -A
git commit -m "Update citations for date $DATE"
git push origin catalog-$DATE
git checkout master
git pull --no-edit origin $BRANCH_NAME
git push origin master
git branch -D $BRANCH_NAME
git push origin --delete $BRANCH_NAME