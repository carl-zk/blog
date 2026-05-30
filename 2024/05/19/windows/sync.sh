#!/bin/bash -ex

echo sync eclipse.pref setting.xml ... to blog

cp /c/Users/Carl/.bashrc /d/blog/source/_posts/windows/
cp /c/Users/Carl/.bash_profile /d/blog/source/_posts/windows/
cp /c/Users/Carl/sync.sh /d/blog/source/_posts/windows/
cp /c/Users/Carl/Documents/eclipse_preferences.epf /d/blog/source/_posts/windows/
cp /c/Users/Carl/Documents/idea_settings.zip /d/blog/source/_posts/windows/
cp /d/local/maven/maven/conf/settings.xml /d/blog/source/_posts/windows/
cp /d/local/maven/maven/conf/toolchains.xml /d/blog/source/_posts/windows/
cp /d/installed/coreDNS/Corefile /d/blog/source/_posts/windows/
cp /d/local/eclipse/eclipse.ini /d/blog/source/_posts/windows/

echo 'done. sync to git? (y/n)'
read
test 'y' = "$REPLY" || exit 0

cd /d/blog
git add .
git commit -m"backup"
git pull origin master
git push origin master

