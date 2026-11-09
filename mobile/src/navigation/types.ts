import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';

export type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
};

export type MainTabParamList = {
  HomeTab: undefined;
  PlannerTab: undefined;
  TasksTab: undefined;
  GoalsTab: undefined;
  ProfileTab: undefined;
};

export type RootStackParamList = {
  Auth: undefined;
  Onboarding: undefined;
  Main: undefined;
  Habits: undefined;
  FinanceDashboard: undefined;
  AddTransaction: { transactionId?: string } | undefined;
  TransactionHistory: undefined;
  TransactionDetail: { transactionId: string };
  AccountsManagement: undefined;
  BudgetManagement: undefined;
  SavingsGoals: undefined;
  FinanceSettings: undefined;
  NotificationCenter: undefined;
  NotificationSettings: undefined;
  ReminderManagement: undefined;
  CreateEditReminder: { reminderId?: string } | undefined;
  LifeAnalytics: undefined;
  ProductivityAnalytics: undefined;
  HabitAnalytics: undefined;
  GoalsAnalytics: undefined;
  FinanceAnalytics: undefined;
  LifeInsights: undefined;
  AutomationDashboard: undefined;
  AutomationTemplates: undefined;
  AutomationDetail: { id: string };
  AutomationApproval: { approval: any };
  AutomationExecutionHistory: { executionId?: string } | undefined;
  PersonalizationSettings: undefined;
  DashboardCustomization: undefined;
  DailyRoutine: undefined;
  Notes: undefined;
  Contacts: undefined;
  Subscriptions: undefined;
  Learning: undefined;
  Travel: undefined;
  Fitness: undefined;
  Assets: undefined;
  Bills: undefined;
  AssignedTasks: undefined;
  MoneyTracking: undefined;
  ItemLending: undefined;
  PersonLedger: { personName: string };
  FocusDashboard: undefined;
};

export type AuthNavigationProp = NativeStackNavigationProp<AuthStackParamList>;
export type RootNavigationProp = NativeStackNavigationProp<RootStackParamList>;
export type MainTabNavigationProp = BottomTabNavigationProp<MainTabParamList>;


