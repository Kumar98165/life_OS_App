import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  SafeAreaContainer,
  Heading,
  BodyText,
  Caption,
  GlassCard,
} from '../../components';
import { usePersonLedger } from '../../hooks/usePeople';
import { PersonActivity } from '../../types/people';

export const PersonLedgerScreen: React.FC = () => {
  const { theme } = useTheme();
  const route = useRoute<any>();
  const personName = route.params?.personName || 'Person';

  const { data: profile, isLoading } = usePersonLedger(personName);

  const renderActivity = ({ item }: { item: PersonActivity }) => (
    <GlassCard style={styles.activityCard}>
      <View style={styles.actRow}>
        <View style={styles.actInfo}>
          <Heading level={3}>{item.summary}</Heading>
          {item.details && <Caption color="secondary">{item.details}</Caption>}
          <Caption color="muted">{new Date(item.activity_date).toLocaleString()}</Caption>
        </View>
        {item.amount != null && (
          <Heading level={3} style={{ color: theme.colors.primary }}>₹{item.amount.toLocaleString()}</Heading>
        )}
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>{personName}</Heading>
          <Caption color="secondary">People Ledger & Unified Profile</Caption>
        </View>

        {profile && (
          <GlassCard style={styles.summaryCard}>
            <View style={styles.statRow}>
              <View style={styles.statCol}>
                <Caption color="secondary">Pending Tasks</Caption>
                <Heading level={2}>{profile.summary.pending_tasks_count}</Heading>
              </View>
              <View style={styles.statCol}>
                <Caption color="secondary">Net Money Balance</Caption>
                <Heading level={2} style={{ color: profile.summary.net_outstanding >= 0 ? '#00C853' : '#FF5252' }}>
                  ₹{Math.abs(profile.summary.net_outstanding).toLocaleString()}
                </Heading>
                <Caption color="muted">{profile.summary.net_outstanding >= 0 ? 'Receivable' : 'Payable'}</Caption>
              </View>
              <View style={styles.statCol}>
                <Caption color="secondary">Unreturned Items</Caption>
                <Heading level={2}>{profile.summary.items_pending_return_count}</Heading>
              </View>
            </View>
          </GlassCard>
        )}

        <Heading level={3} style={styles.sectionTitle}>Activity History</Heading>

        <FlatList
          data={profile?.activity_timeline || []}
          keyExtractor={(item) => item.id}
          renderItem={renderActivity}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <BodyText color="secondary">No activity logged for {personName}</BodyText>
              </View>
            ) : undefined
          }
        />
      </View>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 16 },
  header: { marginVertical: 12 },
  summaryCard: { padding: 16, marginBottom: 16 },
  statRow: { flexDirection: 'row', justifyContent: 'space-around' },
  statCol: { alignItems: 'center' },
  sectionTitle: { marginBottom: 8 },
  list: { paddingBottom: 100 },
  activityCard: { padding: 12, marginBottom: 8 },
  actRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  actInfo: { flex: 1 },
  empty: { alignItems: 'center', marginTop: 40 },
});
