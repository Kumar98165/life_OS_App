import React from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Platform,
  ViewProps,
} from 'react-native';
import { BlurView } from 'expo-blur';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '../../theme';
import { Caption } from '../common/Typography';

export interface TabItem {
  key: string;
  label: string;
  icon: (color: string, focused: boolean) => React.ReactNode;
}

export interface GlassBottomNavigationProps extends ViewProps {
  tabs: TabItem[];
  activeTab: string;
  onTabPress: (key: string) => void;
}

export const GlassBottomNavigation: React.FC<GlassBottomNavigationProps> = ({
  tabs,
  activeTab,
  onTabPress,
  style,
  ...props
}) => {
  const insets = useSafeAreaInsets();
  const { theme, isDark } = useTheme();

  return (
    <View
      style={[
        styles.container,
        {
          paddingBottom: Math.max(insets.bottom, 10),
          borderTopColor: theme.colors.glassBorderSubtle,
          backgroundColor:
            Platform.OS === 'ios'
              ? theme.colors.glassBackgroundMuted
              : theme.colors.glassBackgroundSolid,
        },
        theme.shadows.card,
        style,
      ]}
      {...props}
    >
      {Platform.OS === 'ios' ? (
        <BlurView
          intensity={65}
          tint={isDark ? 'dark' : 'light'}
          style={StyleSheet.absoluteFill}
        />
      ) : null}

      <View style={styles.tabsRow}>
        {tabs.map((tab) => {
          const focused = tab.key === activeTab;
          const activeColor = focused
            ? theme.colors.primary
            : theme.colors.textSecondary;

          return (
            <TouchableOpacity
              key={tab.key}
              onPress={() => onTabPress(tab.key)}
              style={styles.tabButton}
              accessibilityRole="tab"
              accessibilityState={{ selected: focused }}
              accessibilityLabel={tab.label}
            >
              {tab.icon(activeColor, focused)}
              <Caption
                style={[
                  styles.tabLabel,
                  {
                    color: activeColor,
                    fontWeight: focused ? '700' : '500',
                  },
                ]}
              >
                {tab.label}
              </Caption>
              {focused ? (
                <View
                  style={[
                    styles.activePill,
                    { backgroundColor: theme.colors.primary },
                  ]}
                />
              ) : null}
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderTopWidth: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: 60,
  },
  tabsRow: {
    flexDirection: 'row',
    height: 56,
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    minWidth: 44,
  },
  tabLabel: {
    marginTop: 3,
    fontSize: 10,
  },
  activePill: {
    width: 4,
    height: 4,
    borderRadius: 2,
    marginTop: 2,
  },
});

