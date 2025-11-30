/**
 * 從出生年月計算年齡的工具函數
 */

/**
 * 根據出生年份和月份計算當前年齡
 * @param birthYear 出生年份 (例如: 2023)
 * @param birthMonth 出生月份 (1-12)
 * @returns 格式化的年齡字串 (例如: "2歲3個月")
 */
export function calculateAge(birthYear?: number, birthMonth?: number): string {
  if (!birthYear || !birthMonth) {
    return '未知'
  }

  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() + 1 // JavaScript月份從0開始

  // 計算年齡
  let ageYears = currentYear - birthYear
  let ageMonths = currentMonth - birthMonth

  // 如果月份為負數，調整年數和月數
  if (ageMonths < 0) {
    ageYears -= 1
    ageMonths += 12
  }

  // 格式化輸出
  if (ageYears === 0) {
    return `${ageMonths} 個月`
  } else if (ageMonths === 0) {
    return `${ageYears} 歲`
  } else {
    return `${ageYears} 歲 ${ageMonths} 個月`
  }
}

/**
 * 根據出生年份和月份計算總月數
 * @param birthYear 出生年份
 * @param birthMonth 出生月份
 * @returns 總月數
 */
export function calculateAgeInMonths(birthYear?: number, birthMonth?: number): number {
  if (!birthYear || !birthMonth) {
    return 0
  }

  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() + 1

  const ageYears = currentYear - birthYear
  const ageMonths = currentMonth - birthMonth

  return ageYears * 12 + ageMonths
}

/**
 * 從總月數轉換回出生年月
 * @param totalMonths 總月數
 * @returns { birthYear, birthMonth }
 */
export function convertMonthsToBirthDate(totalMonths: number): { birthYear: number; birthMonth: number } {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() + 1

  const birthYear = currentYear - Math.floor(totalMonths / 12)
  let birthMonth = currentMonth - (totalMonths % 12)

  if (birthMonth <= 0) {
    birthMonth += 12
  }

  return { birthYear, birthMonth }
}

/**
 * 直接格式化年齡（當資料庫已經儲存年齡而非出生日期時使用）
 * @param ageYears 年齡（年）
 * @param ageMonths 年齡（月）
 * @returns 格式化的年齡字串 (例如: "2歲3個月")
 */
export function formatAge(ageYears?: number | null, ageMonths?: number | null): string {
  const years = ageYears ?? 0
  const months = ageMonths ?? 0
  
  if (years === 0 && months === 0) {
    return '未滿1個月'
  } else if (years === 0) {
    return `${months} 個月`
  } else if (months === 0) {
    return `${years} 歲`
  } else {
    return `${years} 歲 ${months} 個月`
  }
}
