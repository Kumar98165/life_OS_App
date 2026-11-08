import React, { useState } from 'react';
import { View, StyleSheet, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useAuthStore } from '../../store';
import { useDashboard } from '../../hooks/useDashboard';
import { useUnreadNotificationCount } from '../../hooks/useNotifications';
import { QuickActionType } from '../../components/dashboard/QuickActionsSection';
import {
  SafeAreaContainer,
  ScrollContainer,
  DashboardHeader,
  DailyOverviewCard,
  QuickActionsSection,
  UpcomingScheduleSection,
  TodayTasksSection,
  ActiveGoalsSection,
  HabitSummarySection,
  AIQuickAccessCard,
  FinanceQuickCard,
  AnalyticsQuickCard,
  AlertDialog,
  Toast,
} from '../../components';

export const DashboardScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const { user } = useAuthStore();
  const { dashboardData, isLoading, isError, error, refetch, isRefetching } = useDashboard();
  const { data: unreadCount } = useUnreadNotificationCount();

  const [activeDialog, setActiveDialog] = useState<{
    visible: boolean;
    title: string;
    message: string;
  }>({
    visible: false,
    title: '',
    message: '',
  });

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleAction = (action: QuickActionType) => {
    switch (action) {
      case 'add_task':
        navigation.navigate('TasksTab');
        break;
      case 'plan_day':
        navigation.navigate('PlannerTab');
        break;
      case 'create_goal':
        navigation.navigate('GoalsTab');
        break;
      case 'talk_ai':
        navigation.navigate('AIAssistant');
        break;
    }
  };

  const handleNotificationPress = () => {
    setToastMessage('No new notifications at this time.');
    setTimeout(() => setToastMessage(null), 3000);
  };

  const profileUser = dashboardData?.user || user;
  const progress = dashboardData?.taskProgress || {
    completed: 0,
    total: 0,
    percentage: 0,
    motivationalMessage: 'No tasks scheduled for today. Take time to plan your priorities.',
  };

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
        {/* Header with dynamic greeting and avatar */}
        <DashboardHeader
          userName={profileUser?.full_name}
          onProfilePress={() => navigation.navigate('ProfileTab')}
          onNotificationPress={() => navigation.navigate('NotificationCenter')}
          hasUnreadNotifications={(unreadCount || 0) > 0}
        />

        {/* Daily Tasks Progress Overview */}
        <DailyOverviewCard progress={progress} />

        {/* 4 Core Quick Actions */}
        <QuickActionsSection onActionPress={handleAction} />

        {/* Upcoming Schedule */}
        <UpcomingScheduleSection
          onViewAll={() => navigation.navigate('PlannerTab')}
          onSchedulePress={() => navigation.navigate('PlannerTab')}
        />

        {/* Today's Tasks */}
        <TodayTasksSection
          tasks={dashboardData?.todayTasks || []}
          isLoading={isLoading}
          isError={isError}
          onRetry={refetch}
          onViewAll={() => navigation.navigate('TasksTab')}
          onAddTask={() => navigation.navigate('TasksTab')}
          onTaskPress={() => navigation.navigate('TasksTab')}
        />

        {/* Active Goals */}
        <ActiveGoalsSection
          goals={dashboardData?.activeGoals || []}
          isLoading={isLoading}
          onViewAll={() => navigation.navigate('GoalsTab')}
          onCreateGoal={() => navigation.navigate('GoalsTab')}
        />

        {/* Habits & Streaks */}
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

        {/* Money Management Hub Card */}
        <FinanceQuickCard
          onOpenFinance={() => navigation.navigate('FinanceDashboard')}
        />

        {/* Life Analytics Hub Card */}
        <AnalyticsQuickCard
          onOpenAnalytics={() => navigation.navigate('LifeAnalytics')}
        />

        {/* AI Assistant Card */}
        <AIQuickAccessCard
          onTalkToAI={() => navigation.navigate('AIAssistant')}
        />
      </ScrollContainer>

      {/* Feature notice dialog */}
      <AlertDialog
        visible={activeDialog.visible}
        title={activeDialog.title}
        message={activeDialog.message}
        onDismiss={() => setActiveDialog({ visible: false, title: '', message: '' })}
        buttonLabel="Understood"
      />

      {/* Temporary feedback toast */}
      <Toast visible={!!toastMessage} message={toastMessage || ''} type="info" />
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 8,
    paddingBottom: 100, // Space for bottom navigation bar
  },
});
