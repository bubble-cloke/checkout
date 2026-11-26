with open('index.html', 'r') as f:
    content = f.read()

opens = content.count('<div ')
opens += content.count('<div>')
closes = content.count('</div>')

print('Open divs:', opens)
print('Close divs:', closes)
if opens == closes:
    print('DIV BALANCE: OK')
else:
    print('DIV BALANCE: MISMATCH (diff=' + str(abs(opens-closes)) + ')')

# Check script tags
scripts = content.count('<script')
end_scripts = content.count('</script>')
print('Script tags:', scripts, ' Close:', end_scripts, ' OK' if scripts == end_scripts else ' MISMATCH')