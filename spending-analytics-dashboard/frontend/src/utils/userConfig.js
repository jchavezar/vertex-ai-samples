export const EXECUTIVE_USERS = {
  'ALEXANDER WRIGHT': {
    name: 'Alexander Wright',
    short: 'Alexander',
    tag: 'AW',
    card: '-10041',
    role: 'CEO / Executive',
    color: '#3b82f6',
    badgeClass: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
    avatarBg: 'bg-blue-600/20 border-blue-500/40 text-blue-300',
    dotBg: 'bg-blue-400',
    iconEmoji: '🔵'
  },
  'ELENA VANCE': {
    name: 'Elena Vance',
    short: 'Elena',
    tag: 'EV',
    card: '-82014',
    role: 'CFO / Finance',
    color: '#ec4899',
    badgeClass: 'bg-pink-500/10 text-pink-300 border-pink-500/30',
    avatarBg: 'bg-pink-600/20 border-pink-500/40 text-pink-300',
    dotBg: 'bg-pink-400',
    iconEmoji: '🟣'
  },
  'MARCUS CHEN': {
    name: 'Marcus Chen',
    short: 'Marcus',
    tag: 'MC',
    card: '-49920',
    role: 'CTO / Technology',
    color: '#06b6d4',
    badgeClass: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
    avatarBg: 'bg-cyan-600/20 border-cyan-500/40 text-cyan-300',
    dotBg: 'bg-cyan-400',
    iconEmoji: '🔷'
  },
  'SOPHIA MARTINEZ': {
    name: 'Sophia Martinez',
    short: 'Sophia',
    tag: 'SM',
    card: '-33118',
    role: 'VP Product / Design',
    color: '#a855f7',
    badgeClass: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
    avatarBg: 'bg-purple-600/20 border-purple-500/40 text-purple-300',
    dotBg: 'bg-purple-400',
    iconEmoji: '🟪'
  },
  'DAVID ROSS': {
    name: 'David Ross',
    short: 'David',
    tag: 'DR',
    card: '-77290',
    role: 'VP Operations',
    color: '#10b981',
    badgeClass: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    avatarBg: 'bg-emerald-600/20 border-emerald-500/40 text-emerald-300',
    dotBg: 'bg-emerald-400',
    iconEmoji: '🟢'
  }
};

export const getUserConfig = (memberName = '') => {
  const upper = (memberName || '').toUpperCase();
  for (const [key, val] of Object.entries(EXECUTIVE_USERS)) {
    if (upper.includes(key) || upper.includes(val.short.toUpperCase())) {
      return { fullName: key, ...val };
    }
  }
  
  // Fallback
  const short = memberName.split(' ')[0] || 'User';
  const tag = (memberName || 'EX').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
  return {
    name: memberName || 'Executive Member',
    fullName: memberName || 'Executive Member',
    short,
    tag: tag || 'EX',
    card: '-00000',
    role: 'Executive Member',
    color: '#6366f1',
    badgeClass: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
    avatarBg: 'bg-indigo-600/20 border-indigo-500/40 text-indigo-300',
    dotBg: 'bg-indigo-400',
    iconEmoji: '👤'
  };
};

export const ALL_EXECUTIVE_USERS_LIST = Object.values(EXECUTIVE_USERS);
