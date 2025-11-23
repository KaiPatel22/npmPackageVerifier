import { npmHighImpact } from 'npm-high-impact'

const top30 = npmHighImpact.slice(0, 30)

console.log(JSON.stringify(top30))