// Optional local syntax check: npm install --no-save --no-package-lock --prefix .tooling php-parser
const fs = require('node:fs');
const path = require('node:path');
const parser = require('../.tooling/node_modules/php-parser');
const engine = new parser.Engine({parser: {php7: true, suppressErrors: false}, ast: {withPositions: true}});
const base = path.resolve(__dirname, '../site');
let checked = 0;
function walk(dir) {
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    if (entry.name === 'media') continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.name.endsWith('.php')) {
      engine.parseCode(fs.readFileSync(full, 'utf8'), full);
      checked++;
    }
  }
}
walk(base);
console.log(`PHP syntax parsed: ${checked} files`);
