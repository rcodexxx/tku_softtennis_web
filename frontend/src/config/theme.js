// Naive UI 主題；顏色與 styles/tokens.css 一致（淺色與深色各一組）
const fontSans = "'Noto Sans TC Variable', 'PingFang TC', 'Microsoft JhengHei', -apple-system, sans-serif"
const fontMono = "'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace"

const palettes = {
  light: {
    ink: '#15191c',
    ink2: '#3a4247',
    ink3: '#6b7378',
    line: '#c9cecf',
    lineSoft: '#dde1e2',
    bg: '#eceeed',
    surface: '#f6f7f7',
    surface2: '#ffffff',
    sunk: '#e3e6e6',
    accent: '#ff5a1f',
    accentHover: '#ff7440',
    accentPressed: '#e04a12',
    win: '#1f9d55',
    loss: '#d93b3b'
  },
  dark: {
    ink: '#e6eaec',
    ink2: '#c3cacd',
    ink3: '#7d8a92',
    line: '#2b3640',
    lineSoft: '#1f2830',
    bg: '#0e1215',
    surface: '#141a1f',
    surface2: '#1a2128',
    sunk: '#10161a',
    accent: '#ff7a45',
    accentHover: '#ff9166',
    accentPressed: '#e8622c',
    win: '#3ccf7f',
    loss: '#ff6b6b'
  }
}

export function themeOverridesFor(mode) {
  const c = palettes[mode] ?? palettes.light
  return {
    common: {
      // 主要按鈕用墨色，重點色只留給強調
      primaryColor: c.ink,
      primaryColorHover: c.ink2,
      primaryColorPressed: c.ink,
      primaryColorSuppl: c.ink2,
      infoColor: c.ink2,
      errorColor: c.loss,
      errorColorHover: c.loss,
      errorColorPressed: c.loss,
      successColor: c.win,
      warningColor: c.accent,
      warningColorHover: c.accentHover,
      warningColorPressed: c.accentPressed,
      bodyColor: c.bg,
      cardColor: c.surface,
      modalColor: c.surface,
      popoverColor: c.surface2,
      tableColor: c.surface,
      inputColor: c.surface2,
      textColorBase: c.ink,
      textColor1: c.ink,
      textColor2: c.ink2,
      textColor3: c.ink3,
      borderColor: c.line,
      dividerColor: c.lineSoft,
      borderRadius: '3px',
      borderRadiusSmall: '2px',
      fontFamily: fontSans,
      fontFamilyMono: fontMono,
      fontSize: '16px',
      fontSizeMini: '13px',
      fontSizeTiny: '14px',
      fontSizeSmall: '15px',
      fontSizeMedium: '16px',
      fontSizeLarge: '17px',
      fontSizeHuge: '18px'
    },
    Button: {
      fontWeight: '500',
      borderRadiusMedium: '3px',
      borderRadiusLarge: '3px',
      textColorPrimary: c.bg,
      textColorHoverPrimary: c.bg,
      textColorPressedPrimary: c.bg,
      textColorFocusPrimary: c.bg
    },
    Card: { borderRadius: '4px', borderColor: c.lineSoft },
    Tag: { borderRadius: '2px' },
    DataTable: {
      thColor: c.sunk,
      thTextColor: c.ink2,
      thFontWeight: '500',
      tdColor: c.surface,
      borderColor: c.lineSoft
    },
    Tabs: { tabTextColorActiveLine: c.ink, barColor: c.accent },
    Radio: { buttonColorActive: c.ink, buttonTextColorActive: c.bg, buttonBorderColorActive: c.ink }
  }
}
