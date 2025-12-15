import { npmHighImpact } from 'npm-high-impact'

const top1000 = npmHighImpact.slice(0, 1000)

console.log(JSON.stringify(top1000))