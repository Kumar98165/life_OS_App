import React from 'react';
import { StyleSheet, View } from 'react-native';
import { createBottomTabNavigator, BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { MainTabParamList } from './types';
import {
  DashboardScreen,
  PlannerScreen,
  TasksScreen,
  GoalsScreen,
  HomeScreen as ProfileScreen,
} from '../screens';
import { GlassBottomNavigation, TabItem } from '../components';

const Tab = createBottomTabNavigator<MainTabParamList>();

const TABS: TabItem[] = [
  {
    key: 'HomeTab',
    label: 'Home',
    icon: (color, focused) => (
      <Ionicons name={focused ? 'home' : 'home-outline'} size={22} color={color} />
    ),
  },
  {
    key: 'PlannerTab',
    label: 'Planner',
    icon: (color, focused) => (
      <Ionicons name={focused ? 'calendar' : 'calendar-outline'} size={22} color={color} />
    ),
  },
  {
    key: 'TasksTab',
    label: 'Tasks',
    icon: (color, focused) => (
      <Ionicons name={focused ? 'checkbox' : 'checkbox-outline'} size={22} color={color} />
    ),
  },
  {
    key: 'GoalsTab',
    label: 'Goals',
    icon: (color, focused) => (
      <Ionicons name={focused ? 'flag' : 'flag-outline'} size={22} color={color} />
    ),
  },
  {
    key: 'ProfileTab',
    label: 'Profile',
    icon: (color, focused) => (
      <Ionicons name={focused ? 'person' : 'person-outline'} size={22} color={color} />
    ),
  },
];

const CustomTabBar: React.FC<BottomTabBarProps> = ({ state, navigation }) => {
  const activeRouteName = state.routes[state.index].name;

  const handleTabPress = (key: string) => {
    const isFocused = state.routes[state.index].name === key;
    if (!isFocused) {
      navigation.navigate(key);
    }
  };

  return (
    <GlassBottomNavigation
      tabs={TABS}
      activeTab={activeRouteName}
      onTabPress={handleTabPress}
      style={styles.tabBar}
    />
  );
};

export const MainTabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tab.Screen name="HomeTab" component={DashboardScreen} />
      <Tab.Screen name="PlannerTab" component={PlannerScreen} />
      <Tab.Screen name="TasksTab" component={TasksScreen} />
      <Tab.Screen name="GoalsTab" component={GoalsScreen} />
      <Tab.Screen name="ProfileTab" component={ProfileScreen} />
    </Tab.Navigator>
  );
};

const styles = StyleSheet.create({
  tabBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
});

