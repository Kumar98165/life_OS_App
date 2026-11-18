import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Heading, Caption } from '../common/Typography';
import { GlassCard } from '../glass/GlassCard';

export interface ModuleCategoryGroupProps {
  title: string;
  items: Array<{
    title: string;
    icon: keyof typeof Ionicons.glyphMap;
    route: string;
  }>;
  onNavigate: (route: string) => void;
}

export const ModuleCategoryGroup: React.FC<ModuleCategoryGroupProps> = ({
  title,
  items,
  onNavigate,
}) => {
  const { theme } = useTheme();

  return (
    <GlassCard style={styles.card}>
      <Heading level={3} style={styles.sectionTitle}>
        {title}
      </Heading>

      <View style={styles.grid}>
        {items.map((item) => (
          <TouchableOpacity
            key={item.title}
            style={styles.gridItem}
            activeOpacity={0.7}
            onPress={() => onNavigate(item.route)}
          >
            {/* Unified Single Color matching Login/Theme */}
            <View
              style={[
                styles.iconCircle,
                {
                  backgroundColor: theme.colors.surfaceSubtle,
                  borderColor: theme.colors.border,
                },
              ]}
            >
              <Ionicons
                name={item.icon}
                size={22}
                color={theme.colors.primary}
              />
            </View>
            <Caption weight="600" numberOfLines={1} align="center" style={styles.itemTitle}>
              {item.title}
            </Caption>
          </TouchableOpacity>
        ))}
      </View>
    </GlassCard>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 18,
    marginBottom: 16,
    borderRadius: 20,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 16,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    rowGap: 16,
  },
  gridItem: {
    width: '25%',
    alignItems: 'center',
    paddingHorizontal: 4,
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 6,
  },
  itemTitle: {
    fontSize: 11,
  },
});
