# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

### Lazy Git
$msg = "Chris Brennan, chris@brennantechnologies.com $(Get-Date)"
$msg

git add .
git commit -m $msg
git push


