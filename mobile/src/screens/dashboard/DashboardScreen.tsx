import React, { useState } from 'react';
import { View, StyleSheet, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useAuthStore } from '../../store';
import { useDashboard } from '../../hooks/useDashboard';
import { useUnreadNotificationCount } from '../../hooks/useNotifications';
import { useDashboardPreferences } from '../../hooks/usePersonalization';
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
  FinanceQuickCard,
  AnalyticsQuickCard,
  ProductivityModuleHub,
  AlertDialog,
  Toast,
} from '../../components';

export const DashboardScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const { user } = useAuthStore();
  const { dashboardData, isLoading, isError, error, refetch, isRefetching } = useDashboard();
  const { data: unreadCount } = useUnreadNotificationCount();
  const { data: dashboardPrefs } = useDashboardPreferences();

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
      case 'focus':
        navigation.navigate('FocusDashboard');
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

  // Resolve widget ordering & visibility from personalization
  const configuredWidgets = dashboardPrefs?.dashboard_widgets || [
    { id: 'daily_overview', visible: true, order: 0 },
    { id: 'quick_actions', visible: true, order: 1 },
    { id: 'upcoming_schedule', visible: true, order: 2 },
    { id: 'today_tasks', visible: true, order: 3 },
    { id: 'active_goals', visible: true, order: 4 },
    { id: 'habit_summary', visible: true, order: 5 },
    { id: 'finance_quick', visible: true, order: 6 },
    { id: 'analytics_quick', visible: true, order: 7 },
    { id: 'ai_quick_access', visible: true, order: 8 },
  ];

  const widgetMap: Record<string, boolean> = {};
  configuredWidgets.forEach((w) => {
    widgetMap[w.id] = w.visible;
  });

  const sortedWidgetIds = [...configuredWidgets]
    .sort((a, b) => a.order - b.order)
    .filter((w) => w.visible)
    .map((w) => w.id);

  const renderWidget = (id: string) => {
    switch (id) {
      case 'daily_overview':
        return <DailyOverviewCard key={id} progress={progress} />;
      case 'quick_actions':
        return <QuickActionsSection key={id} onActionPress={handleAction} />;
      case 'upcoming_schedule':
        return (
          <UpcomingScheduleSection
            key={id}
            onViewAll={() => navigation.navigate('PlannerTab')}
            onSchedulePress={() => navigation.navigate('PlannerTab')}
          />
        );
      case 'today_tasks':
        return (
          <TodayTasksSection
            key={id}
            tasks={dashboardData?.todayTasks || []}
            isLoading={isLoading}
            isError={isError}
            onRetry={refetch}
            onViewAll={() => navigation.navigate('TasksTab')}
            onAddTask={() => navigation.navigate('TasksTab')}
            onTaskPress={() => navigation.navigate('TasksTab')}
          />
        );
      case 'active_goals':
        return (
          <ActiveGoalsSection
            key={id}
            goals={dashboardData?.activeGoals || []}
            isLoading={isLoading}
            onViewAll={() => navigation.navigate('GoalsTab')}
            onCreateGoal={() => navigation.navigate('GoalsTab')}
          />
        );
      case 'habit_summary':
        return (
          <HabitSummarySection
            key={id}
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
        );
      case 'finance_quick':
        return (
          <FinanceQuickCard
            key={id}
            onOpenFinance={() => navigation.navigate('FinanceDashboard')}
          />
        );
      case 'analytics_quick':
        return (
          <AnalyticsQuickCard
            key={id}
            onOpenAnalytics={() => navigation.navigate('LifeAnalytics')}
          />
        );
      default:
        return null;
    }
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
          onCustomizePress={() => navigation.navigate('DashboardCustomization')}
          hasUnreadNotifications={(unreadCount || 0) > 0}
        />

        {/* Productivity Hub Quick Links */}
        <ProductivityModuleHub onNavigate={(route) => navigation.navigate(route)} />

        {/* Dynamic Personalized Widget List */}
        {sortedWidgetIds.map(renderWidget)}
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
