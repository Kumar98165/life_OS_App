import React, { useState } from 'react';
import { View, StyleSheet, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useAuthStore } from '../../store';
import { useDashboard } from '../../hooks/useDashboard';
import { useUnreadNotificationCount } from '../../hooks/useNotifications';
import {
  SafeAreaContainer,
  ScrollContainer,
  ModernDashboardHeader,
  DashboardTopSummaryCard,
  ModuleCategoryGroup,
  DailyOverviewCard,
  UpcomingScheduleSection,
  TodayTasksSection,
  ActiveGoalsSection,
  HabitSummarySection,
  AlertDialog,
  Toast,
} from '../../components';

export const DashboardScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const { user } = useAuthStore();
  const { dashboardData, isLoading, isError, refetch, isRefetching } = useDashboard();
  const { data: unreadCount } = useUnreadNotificationCount();

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const profileUser = dashboardData?.user || user;
  const progress = dashboardData?.taskProgress || {
    completed: 0,
    total: 0,
    percentage: 0,
    motivationalMessage: 'No tasks scheduled for today. Take time to plan your priorities.',
  };

  // Structured Grid Categories (Single unified color matching Login Theme)
  const utilityServices = [
    { title: 'Bills', icon: 'receipt-outline' as const, route: 'Bills' },
    { title: 'Subs', icon: 'card-outline' as const, route: 'Subscriptions' },
    { title: 'Lending', icon: 'cash-outline' as const, route: 'MoneyTracking' },
    { title: 'Borrow', icon: 'swap-horizontal-outline' as const, route: 'ItemLending' },
    { title: 'Assigned', icon: 'clipboard-outline' as const, route: 'AssignedTasks' },
    { title: 'Assets', icon: 'cube-outline' as const, route: 'Assets' },
    { title: 'Contacts', icon: 'people-outline' as const, route: 'Contacts' },
    { title: 'Notes', icon: 'document-text-outline' as const, route: 'Notes' },
  ];

  const lifestyleServices = [
    { title: 'Focus Timer', icon: 'timer-outline' as const, route: 'FocusDashboard' },
    { title: 'Fitness', icon: 'barbell-outline' as const, route: 'Fitness' },
    { title: 'Learning', icon: 'school-outline' as const, route: 'Learning' },
    { title: 'Travel', icon: 'airplane-outline' as const, route: 'Travel' },
  ];

  return (
    <SafeAreaContainer edges={['top']}>
      <ScrollContainer
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={() => {
              refetch();
            }}
            tintColor={theme.colors.primary}
            colors={[theme.colors.primary]}
          />
        }
      >
        {/* Modern Top Header (Profile + Greeting + Notification Icon) */}
        <ModernDashboardHeader
          userName={profileUser?.full_name}
          onProfilePress={() => navigation.navigate('ProfileTab')}
          onNotificationPress={() => navigation.navigate('NotificationCenter')}
          onSearchPress={() => navigation.navigate('TasksTab')}
          hasUnreadNotifications={(unreadCount || 0) > 0}
        />

        {/* Top Summary Card (Wallet Net Balance + Life Score + Quick Hub Icons) */}
        <DashboardTopSummaryCard
          balanceFormatted="₹0.00"
          rewardPoints="100"
          onNavigateModule={(route) => navigation.navigate(route)}
        />

        {/* Category Group 1: Utility & Personal Ledger */}
        <ModuleCategoryGroup
          title="Productivity & Records"
          items={utilityServices}
          onNavigate={(route) => navigation.navigate(route)}
        />

        {/* Category Group 2: Lifestyle & Growth */}
        <ModuleCategoryGroup
          title="Lifestyle & Habits"
          items={lifestyleServices}
          onNavigate={(route) => navigation.navigate(route)}
        />

        {/* Overview Stats (Read-Only Status Updates) */}
        <DailyOverviewCard progress={progress} />

        {/* Upcoming Schedule (View only from dashboard) */}
        <UpcomingScheduleSection
          onViewAll={() => navigation.navigate('PlannerTab')}
          onSchedulePress={() => navigation.navigate('PlannerTab')}
        />

        {/* Today's Tasks Summary */}
        <TodayTasksSection
          tasks={dashboardData?.todayTasks || []}
          isLoading={isLoading}
          isError={isError}
          onRetry={refetch}
          onViewAll={() => navigation.navigate('TasksTab')}
          onTaskPress={() => navigation.navigate('TasksTab')}
        />

        {/* Habits Status */}
        <HabitSummarySection
          summary={
            dashboardData?.habitSummary || {
              activeCount: 0,
              completedTodayCount: 0,
              completionRate: 0,
            }
          }
          onViewAll={() => navigation.navigate('Habits')}
          onTrackHabit={() => navigation.navigate('Habits')}
        />

        {/* Active Goals Status */}
        <ActiveGoalsSection
          goals={dashboardData?.activeGoals || []}
          isLoading={isLoading}
          onViewAll={() => navigation.navigate('GoalsTab')}
          onGoalPress={() => navigation.navigate('GoalsTab')}
        />
      </ScrollContainer>

      {/* Temporary feedback toast */}
      <Toast visible={!!toastMessage} message={toastMessage || ''} type="info" />
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 4,
    paddingBottom: 110, // Generous spacing for bottom nav bar
  },
});
