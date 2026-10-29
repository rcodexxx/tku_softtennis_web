// Naive UI 主題；顏色與 styles/tokens.css 一致
const blue = { 700: '#163a80', 600: '#1f4fa8', 800: '#10306f' }
const red = '#e5383f'
const fontSans = "'Noto Sans TC Variable', 'PingFang TC', 'Microsoft JhengHei', -apple-system, sans-serif"

export const themeOverrides = {
  common: {
    primaryColor: blue[700],
    primaryColorHover: blue[600],
    primaryColorPressed: blue[800],
    primaryColorSuppl: blue[600],
    errorColor: red,
    errorColorHover: '#ec5a60',
    errorColorPressed: '#d6232a',
    successColor: '#16a34a',
    warningColor: '#f2b705',
    bodyColor: '#f4f6fb',
    textColorBase: '#111827',
    textColor1: '#111827',
    textColor2: '#374151',
    textColor3: '#6b7280',
    borderColor: '#e5e9f2',
    dividerColor: '#e5e9f2',
    borderRadius: '10px',
    borderRadiusSmall: '8px',
    fontFamily: fontSans,
    fontSize: '14px'
  },
  Card: { borderRadius: '18px', borderColor: '#e5e9f2' },
  Button: { fontWeight: '600', borderRadiusMedium: '10px', borderRadiusLarge: '12px' },
  Tag: { borderRadius: '999px' },
  DataTable: { thColor: '#f3f6fd', thTextColor: '#374151', thFontWeight: '600' }
}
