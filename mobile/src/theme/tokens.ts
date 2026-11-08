export const opacity = {
  transparent: 0,
  subtle: 0.1,
  muted: 0.25,
  medium: 0.5,
  glass: 0.75,
  glassSolid: 0.9,
  opaque: 1,
} as const;

export const animation = {
  durations: {
    instant: 100,
    fast: 200,
    normal: 300,
    slow: 500,
  },
  scale: {
    pressed: 0.97,
    active: 0.98,
    normal: 1,
  },
} as const;

export const zIndex = {
  base: 0,
  card: 10,
  floating: 20,
  header: 50,
  bottomBar: 60,
  modal: 100,
  toast: 200,
} as const;

