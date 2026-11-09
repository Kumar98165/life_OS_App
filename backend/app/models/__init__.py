from app.models.base import BaseModel, utc_now
from app.models.user import User
from app.models.auth_token import RefreshToken
from app.models.user_preference import UserPreference
from app.models.task import TaskCategory, Task
from app.models.goal import Goal, GoalMilestone
from app.models.habit import Habit, HabitLog
from app.models.planner import PlannerBlock
from app.models.note import Note, NoteTag, note_tag_association
from app.models.finance import (
    FinancialAccount,
    FinancialCategory,
    FinancialTransaction,
    Budget,
    SavingsGoal,
    SavingsGoalContribution,
)
from app.models.notification import (
    Notification,
    NotificationPreference,
    Reminder,
    PushDeviceToken,
    NotificationDelivery,
)
from app.models.automation import (
    AutomationDefinition,
    AutomationExecution,
    AutomationAction,
    AutomationApproval,
    AutomationExecutionLog,
)
from app.models.personalization import UserPersonalization, DailyRoutine, DEFAULT_DASHBOARD_WIDGETS
from app.models.activity_log import ActivityLog
from app.models.extensions import (
    NoteFolder,
    NoteAttachment,
    Contact,
    ContactInteraction,
    Subscription,
    LearningGoal,
    StudySession,
    Trip,
    TripItineraryItem,
    TripPackingItem,
    Workout,
    PersonalAsset,
    AssetMaintenanceRecord,
    Bill,
    BillPayment,
)
from app.models.people_tracking import (
    AssignedTask,
    TaskFollowUp,
    MoneyTransaction,
    MoneyRepayment,
    PersonalItem,
    ItemLendingRecord,
    PersonActivity,
)
from app.models.focus import FocusGoal, FocusSession, FocusDistraction

__all__ = [
    "BaseModel",
    "utc_now",
    "User",
    "RefreshToken",
    "UserPreference",
    "UserPersonalization",
    "DailyRoutine",
    "DEFAULT_DASHBOARD_WIDGETS",
    "TaskCategory",
    "Task",
    "Goal",
    "GoalMilestone",
    "Habit",
    "HabitLog",
    "PlannerBlock",
    "Note",
    "NoteTag",
    "note_tag_association",
    "NoteFolder",
    "NoteAttachment",
    "Contact",
    "ContactInteraction",
    "Subscription",
    "LearningGoal",
    "StudySession",
    "Trip",
    "TripItineraryItem",
    "TripPackingItem",
    "Workout",
    "PersonalAsset",
    "AssetMaintenanceRecord",
    "Bill",
    "BillPayment",
    "AssignedTask",
    "TaskFollowUp",
    "MoneyTransaction",
    "MoneyRepayment",
    "PersonalItem",
    "ItemLendingRecord",
    "PersonActivity",
    "FocusGoal",
    "FocusSession",
    "FocusDistraction",
    "FinancialAccount",
    "FinancialCategory",
    "FinancialTransaction",
    "Budget",
    "SavingsGoal",
    "SavingsGoalContribution",
    "Notification",
    "NotificationPreference",
    "Reminder",
    "PushDeviceToken",
    "NotificationDelivery",
    "AutomationDefinition",
    "AutomationExecution",
    "AutomationAction",
    "AutomationApproval",
    "AutomationExecutionLog",
    "ActivityLog",
]
