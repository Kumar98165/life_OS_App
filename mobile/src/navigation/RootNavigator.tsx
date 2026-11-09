import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../store';
import { AuthNavigator } from './AuthNavigator';
import { MainTabNavigator } from './MainTabNavigator';
import {
  OnboardingScreen,
  SplashScreen,
  HabitsScreen,
  FinanceDashboardScreen,
  AddTransactionScreen,
  TransactionHistoryScreen,
  TransactionDetailScreen,
  AccountsScreen,
  BudgetManagementScreen,
  SavingsGoalsScreen,
  FinanceSettingsScreen,
  NotificationCenterScreen,
  NotificationSettingsScreen,
  ReminderManagementScreen,
  CreateEditReminderScreen,
  LifeAnalyticsScreen,
  ProductivityAnalyticsScreen,
  HabitAnalyticsScreen,
  GoalsAnalyticsScreen,
  FinanceAnalyticsScreen,
  LifeInsightsScreen,
  AutomationDashboardScreen,
  AutomationTemplatesScreen,
  AutomationDetailScreen,
  AutomationApprovalScreen,
  AutomationExecutionHistoryScreen,
  PersonalizationSettingsScreen,
  DashboardCustomizationScreen,
  DailyRoutineScreen,
  NotesScreen,
  ContactsScreen,
  SubscriptionsScreen,
  LearningScreen,
  TravelScreen,
  FitnessScreen,
  AssetsScreen,
  BillsScreen,
  AssignedTasksScreen,
  MoneyScreen,
  ItemLendingScreen,
  PersonLedgerScreen,
} from '../screens';
import { RootStackParamList } from './types';
const Stack = createNativeStackNavigator<RootStackParamList>();
export const RootNavigator: React.FC = () => {
  const {
    isAuthenticated,
    isRestoringSession,
    hasCompletedOnboarding,
    restoreSession,
  } = useAuthStore();

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  if (isRestoringSession) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          animation: 'fade',
        }}
      >
        {!isAuthenticated ? (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        ) : !hasCompletedOnboarding ? (
          <Stack.Screen name="Onboarding" component={OnboardingScreen} />
        ) : (
          <>
            <Stack.Screen name="Main" component={MainTabNavigator} />
            <Stack.Screen
              name="Habits"
              component={HabitsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="FinanceDashboard"
              component={FinanceDashboardScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="AddTransaction"
              component={AddTransactionScreen}
              options={{ animation: 'slide_from_bottom' }}
            />
            <Stack.Screen
              name="TransactionHistory"
              component={TransactionHistoryScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="TransactionDetail"
              component={TransactionDetailScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="AccountsManagement"
              component={AccountsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="BudgetManagement"
              component={BudgetManagementScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="SavingsGoals"
              component={SavingsGoalsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="FinanceSettings"
              component={FinanceSettingsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="NotificationCenter"
              component={NotificationCenterScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="NotificationSettings"
              component={NotificationSettingsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="ReminderManagement"
              component={ReminderManagementScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="CreateEditReminder"
              component={CreateEditReminderScreen}
              options={{ animation: 'slide_from_bottom' }}
            />
            <Stack.Screen
              name="LifeAnalytics"
              component={LifeAnalyticsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="ProductivityAnalytics"
              component={ProductivityAnalyticsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="HabitAnalytics"
              component={HabitAnalyticsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="GoalsAnalytics"
              component={GoalsAnalyticsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="FinanceAnalytics"
              component={FinanceAnalyticsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="LifeInsights"
              component={LifeInsightsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="AutomationDashboard"
              component={AutomationDashboardScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="AutomationTemplates"
              component={AutomationTemplatesScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="AutomationDetail"
              component={AutomationDetailScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="AutomationApproval"
              component={AutomationApprovalScreen}
              options={{ animation: 'slide_from_bottom' }}
            />
            <Stack.Screen
              name="AutomationExecutionHistory"
              component={AutomationExecutionHistoryScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="PersonalizationSettings"
              component={PersonalizationSettingsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="DashboardCustomization"
              component={DashboardCustomizationScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="DailyRoutine"
              component={DailyRoutineScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Notes"
              component={NotesScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Contacts"
              component={ContactsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Subscriptions"
              component={SubscriptionsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Learning"
              component={LearningScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Travel"
              component={TravelScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Fitness"
              component={FitnessScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Assets"
              component={AssetsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="Bills"
              component={BillsScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="AssignedTasks"
              component={AssignedTasksScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="MoneyTracking"
              component={MoneyScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="ItemLending"
              component={ItemLendingScreen}
              options={{ animation: 'slide_from_right' }}
            />
            <Stack.Screen
              name="PersonLedger"
              component={PersonLedgerScreen}
              options={{ animation: 'slide_from_right' }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

