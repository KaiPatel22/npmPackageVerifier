import { npmHighImpact } from 'npm-high-impact'

const top2000 = npmHighImpact.slice(0, 2000)

console.log(JSON.stringify(top2000))