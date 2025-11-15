import { npmHighImpact } from 'npm-high-impact'

const top20 = npmHighImpact.slice(0, 20)

console.log(JSON.stringify(top20))