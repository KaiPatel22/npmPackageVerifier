import { npmHighImpact } from 'npm-high-impact'

const top = npmHighImpact.slice(0, 6000)

console.log(JSON.stringify(top))