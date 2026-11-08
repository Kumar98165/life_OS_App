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
  AIAssistant: { conversationId?: string } | undefined;
  AIMemory: undefined;
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
  VoiceAssistant: undefined;
  VoiceSettings: undefined;
};

export type AuthNavigationProp = NativeStackNavigationProp<AuthStackParamList>;
export type RootNavigationProp = NativeStackNavigationProp<RootStackParamList>;
export type MainTabNavigationProp = BottomTabNavigationProp<MainTabParamList>;


