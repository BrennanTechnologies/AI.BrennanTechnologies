### Lazy Git
$msg = "Chris Brennan, chris@brennantechnologies.com $(Get-Date)"
$msg

git add .
git commit -m $msg
git push

