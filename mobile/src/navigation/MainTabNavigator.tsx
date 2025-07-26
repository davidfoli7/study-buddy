import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { MainTabParamList, LearnStackParamList, AssessStackParamList } from '../types';
import DashboardScreen from '../screens/DashboardScreen';
import LearnHomeScreen from '../screens/learn/LearnHomeScreen';
import SubjectSelectScreen from '../screens/learn/SubjectSelectScreen';
import ContentListScreen from '../screens/learn/ContentListScreen';
import ContentViewerScreen from '../screens/learn/ContentViewerScreen';
import LearningSessionScreen from '../screens/learn/LearningSessionScreen';
import AssessHomeScreen from '../screens/assess/AssessHomeScreen';
import AssessmentListScreen from '../screens/assess/AssessmentListScreen';
import AssessmentScreen from '../screens/assess/AssessmentScreen';
import AssessmentResultsScreen from '../screens/assess/AssessmentResultsScreen';
import ProgressScreen from '../screens/ProgressScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Tab = createBottomTabNavigator<MainTabParamList>();
const LearnStack = createStackNavigator<LearnStackParamList>();
const AssessStack = createStackNavigator<AssessStackParamList>();

// Learn Stack Navigator
const LearnNavigator: React.FC = () => {
  return (
    <LearnStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#6366f1',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <LearnStack.Screen 
        name="LearnHome" 
        component={LearnHomeScreen}
        options={{ title: 'Learn' }}
      />
      <LearnStack.Screen 
        name="SubjectSelect" 
        component={SubjectSelectScreen}
        options={{ title: 'Select Subject' }}
      />
      <LearnStack.Screen 
        name="ContentList" 
        component={ContentListScreen}
        options={{ title: 'Learning Content' }}
      />
      <LearnStack.Screen 
        name="ContentViewer" 
        component={ContentViewerScreen}
        options={{ title: 'Content' }}
      />
      <LearnStack.Screen 
        name="LearningSession" 
        component={LearningSessionScreen}
        options={{ title: 'Study Session' }}
      />
    </LearnStack.Navigator>
  );
};

// Assessment Stack Navigator
const AssessNavigator: React.FC = () => {
  return (
    <AssessStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#f59e0b',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <AssessStack.Screen 
        name="AssessHome" 
        component={AssessHomeScreen}
        options={{ title: 'Assessments' }}
      />
      <AssessStack.Screen 
        name="AssessmentList" 
        component={AssessmentListScreen}
        options={{ title: 'Available Tests' }}
      />
      <AssessStack.Screen 
        name="Assessment" 
        component={AssessmentScreen}
        options={{ title: 'Assessment' }}
      />
      <AssessStack.Screen 
        name="AssessmentResults" 
        component={AssessmentResultsScreen}
        options={{ title: 'Results' }}
      />
    </AssessStack.Navigator>
  );
};

// Main Tab Navigator
const MainTabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Learn':
              iconName = 'school';
              break;
            case 'Assess':
              iconName = 'quiz';
              break;
            case 'Progress':
              iconName = 'trending-up';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'home';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6366f1',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: 'Dashboard' }}
      />
      <Tab.Screen 
        name="Learn" 
        component={LearnNavigator}
        options={{ title: 'Learn' }}
      />
      <Tab.Screen 
        name="Assess" 
        component={AssessNavigator}
        options={{ title: 'Test' }}
      />
      <Tab.Screen 
        name="Progress" 
        component={ProgressScreen}
        options={{ title: 'Progress' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
};

export default MainTabNavigator;