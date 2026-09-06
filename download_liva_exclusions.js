const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');
const files = [
  ['Inayah Excluded Providers Aug 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/Inayah%20-%20Excluded%20Providers%20List%20-%20Aug%20-%202026.xlsx'],
  ['NAS Excluded Providers Aug 2026.pdf', 'https://www.livainsurance.ae/sites/default/files/2026-08/NAS%20-%20Excluded%20Providers%20and%20Professionals%20-%20Aug%20-%202026.pdf'],
  ['Neuron Excluded Providers Aug 2026.pdf', 'https://www.livainsurance.ae/sites/default/files/2026-08/Neuron%20-%20Excluded%20Providers%20and%20Professionals%20-%20Aug%20-%202026.pdf'],
  ['Al Madallah Excluded Providers Aug 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/Al%20Madallah%20-%20Excluded%20Providers%20List%20-%20Aug%20-%202026.xlsx'],
  ['Mednet Excluded Providers Aug 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/Mednet%20-%20Excluded%20Providers%20List%20-%20Aug%20-%202026.xlsx'],
  ['Nextcare Excluded Providers Aug 2026.pdf', 'https://www.livainsurance.ae/sites/default/files/2026-08/Nextcare%20-%20Excluded%20Providers%20List%20-%20Aug%20-%202026.pdf'],
];
(async()=>{const b=await chromium.launch({headless:true,executablePath:'/snap/bin/brave',args:['--no-sandbox']});const c=await b.newContext();try{for(const [n,u] of files){const r=await c.request.get(u,{timeout:60000});console.log(n,r.status());if(r.ok())fs.writeFileSync(`sources/raw/Liva ${n}`,await r.body())}}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
