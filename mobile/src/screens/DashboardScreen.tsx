import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  SafeAreaView,
  RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LineChart, PieChart } from 'react-native-chart-kit';

import { RootState, AppDispatch } from '../store';

const { width: screenWidth } = Dimensions.get('window');

const DashboardScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useSelector((state: RootState) => state.auth);
  const [refreshing, setRefreshing] = useState(false);

  // Mock data - in real app, this would come from Redux store
  const weeklyProgress = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        data: [30, 45, 60, 40, 75, 90, 55],
        color: (opacity = 1) => `rgba(99, 102, 241, ${opacity})`,
        strokeWidth: 3,
      },
    ],
  };

  const subjectProgress = [
    {
      name: 'Mathematics',
      population: 75,
      color: '#6366f1',
      legendFontColor: '#333',
      legendFontSize: 12,
    },
    {
      name: 'Science',
      population: 60,
      color: '#10b981',
      legendFontColor: '#333',
      legendFontSize: 12,
    },
    {
      name: 'English',
      population: 85,
      color: '#f59e0b',
      legendFontColor: '#333',
      legendFontSize: 12,
    },
    {
      name: 'History',
      population: 45,
      color: '#ef4444',
      legendFontColor: '#333',
      legendFontSize: 12,
    },
  ];

  const todayRecommendations = [
    {
      id: 1,
      type: 'study',
      title: 'Review Algebra Concepts',
      description: 'Focus on quadratic equations',
      estimatedTime: 30,
      priority: 'high',
    },
    {
      id: 2,
      type: 'assessment',
      title: 'Science Quiz',
      description: 'Test your knowledge of photosynthesis',
      estimatedTime: 15,
      priority: 'medium',
    },
    {
      id: 3,
      type: 'break',
      title: 'Take a Break',
      description: 'You\'ve been studying for 90 minutes',
      estimatedTime: 10,
      priority: 'low',
    },
  ];

  const onRefresh = async () => {
    setRefreshing(true);
    // Fetch latest data
    setTimeout(() => {
      setRefreshing(false);
    }, 2000);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      default:
        return '#10b981';
    }
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'study':
        return 'school';
      case 'assessment':
        return 'quiz';
      case 'break':
        return 'coffee';
      default:
        return 'lightbulb';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>
              {getGreeting()}, {user?.fullName?.split(' ')[0] || 'Student'}!
            </Text>
            <Text style={styles.subtitle}>Ready to learn something new?</Text>
          </View>
          <TouchableOpacity style={styles.profileButton}>
            <Icon name="person" size={24} color="#6366f1" />
          </TouchableOpacity>
        </View>

        {/* Study Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Icon name="schedule" size={24} color="#6366f1" />
            <Text style={styles.statNumber}>{user?.totalStudyTimeMinutes || 0}</Text>
            <Text style={styles.statLabel}>Minutes Today</Text>
          </View>
          <View style={styles.statCard}>
            <Icon name="trending-up" size={24} color="#10b981" />
            <Text style={styles.statNumber}>{user?.streakDays || 0}</Text>
            <Text style={styles.statLabel}>Day Streak</Text>
          </View>
          <View style={styles.statCard}>
            <Icon name="star" size={24} color="#f59e0b" />
            <Text style={styles.statNumber}>{user?.averageScore?.toFixed(1) || '0.0'}%</Text>
            <Text style={styles.statLabel}>Avg Score</Text>
          </View>
        </View>

        {/* Weekly Progress Chart */}
        <View style={styles.chartContainer}>
          <Text style={styles.sectionTitle}>Weekly Study Progress</Text>
          <LineChart
            data={weeklyProgress}
            width={screenWidth - 40}
            height={200}
            chartConfig={{
              backgroundColor: '#ffffff',
              backgroundGradientFrom: '#ffffff',
              backgroundGradientTo: '#ffffff',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(99, 102, 241, ${opacity})`,
              labelColor: (opacity = 1) => `rgba(51, 51, 51, ${opacity})`,
              style: {
                borderRadius: 16,
              },
              propsForDots: {
                r: '6',
                strokeWidth: '2',
                stroke: '#6366f1',
              },
            }}
            bezier
            style={styles.chart}
          />
        </View>

        {/* Subject Progress */}
        <View style={styles.chartContainer}>
          <Text style={styles.sectionTitle}>Subject Mastery</Text>
          <PieChart
            data={subjectProgress}
            width={screenWidth - 40}
            height={200}
            chartConfig={{
              color: (opacity = 1) => `rgba(99, 102, 241, ${opacity})`,
            }}
            accessor="population"
            backgroundColor="transparent"
            paddingLeft="15"
            absolute
          />
        </View>

        {/* Today's Recommendations */}
        <View style={styles.recommendationsContainer}>
          <Text style={styles.sectionTitle}>Recommended for You</Text>
          {todayRecommendations.map((recommendation) => (
            <TouchableOpacity
              key={recommendation.id}
              style={styles.recommendationCard}
              onPress={() => {
                // Navigate based on recommendation type
                if (recommendation.type === 'study') {
                  navigation.navigate('Learn' as never);
                } else if (recommendation.type === 'assessment') {
                  navigation.navigate('Assess' as never);
                }
              }}
            >
              <View style={styles.recommendationHeader}>
                <Icon
                  name={getRecommendationIcon(recommendation.type)}
                  size={24}
                  color="#6366f1"
                />
                <View
                  style={[
                    styles.priorityDot,
                    { backgroundColor: getPriorityColor(recommendation.priority) },
                  ]}
                />
              </View>
              <Text style={styles.recommendationTitle}>{recommendation.title}</Text>
              <Text style={styles.recommendationDescription}>
                {recommendation.description}
              </Text>
              <View style={styles.recommendationFooter}>
                <Text style={styles.estimatedTime}>
                  ~{recommendation.estimatedTime} min
                </Text>
                <Icon name="arrow-forward" size={16} color="#6b7280" />
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActionsContainer}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            <TouchableOpacity
              style={[styles.quickActionCard, { backgroundColor: '#6366f1' }]}
              onPress={() => navigation.navigate('Learn' as never)}
            >
              <Icon name="school" size={32} color="#ffffff" />
              <Text style={styles.quickActionText}>Start Learning</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.quickActionCard, { backgroundColor: '#10b981' }]}
              onPress={() => navigation.navigate('Assess' as never)}
            >
              <Icon name="quiz" size={32} color="#ffffff" />
              <Text style={styles.quickActionText}>Take Quiz</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.quickActionCard, { backgroundColor: '#f59e0b' }]}
              onPress={() => navigation.navigate('Progress' as never)}
            >
              <Icon name="trending-up" size={32} color="#ffffff" />
              <Text style={styles.quickActionText}>View Progress</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.quickActionCard, { backgroundColor: '#8b5cf6' }]}
              onPress={() => navigation.navigate('Profile' as never)}
            >
              <Icon name="settings" size={32} color="#ffffff" />
              <Text style={styles.quickActionText}>Settings</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 4,
  },
  profileButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 15,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  chartContainer: {
    backgroundColor: '#ffffff',
    margin: 20,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16,
  },
  chart: {
    borderRadius: 16,
  },
  recommendationsContainer: {
    margin: 20,
  },
  recommendationCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  priorityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  recommendationDescription: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 12,
  },
  recommendationFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  estimatedTime: {
    fontSize: 12,
    color: '#6b7280',
  },
  quickActionsContainer: {
    margin: 20,
    marginBottom: 40,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 15,
  },
  quickActionCard: {
    width: (screenWidth - 55) / 2,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 100,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 8,
  },
});

export default DashboardScreen;