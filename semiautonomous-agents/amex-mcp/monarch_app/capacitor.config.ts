import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.jchavezar.monarch.amethyst',
  appName: 'Monarch Amethyst',
  webDir: '.',
  bundledWebRuntime: false,
  ios: {
    contentInset: 'always',
    preferredContentMode: 'mobile',
    backgroundColor: '#0B0914'
  },
  android: {
    backgroundColor: '#0B0914',
    allowMixedContent: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 1200,
      backgroundColor: '#7C3AED',
      showSpinner: false
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#7C3AED'
    }
  }
};

export default config;
