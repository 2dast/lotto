// 로또 번호 구간 인덱스: 0 = 1-10, 1 = 11-20, 2 = 21-30, 3 = 31-40, 4 = 41-45.
// 대시보드(index.astro)와 리포트(components/chartMath.ts)가 같은 구간 규칙을 쓰도록 한 곳에 둔다.
export function ballZoneIndex(n: number): number {
  return Math.min(Math.max(Math.floor((n - 1) / 10), 0), 4);
}
