import { npmHighImpact } from 'npm-high-impact'

const top100 = npmHighImpact.slice(0, 100)

console.log(JSON.stringify(top100))