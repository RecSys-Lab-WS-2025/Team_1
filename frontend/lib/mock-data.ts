// Mock data for TrailSaga prototype
//
// NOTE: When connecting to the real backend API, use the types from api-types.ts
// and transform the data accordingly. Specifically:
// - xpReward should come from ApiRoute.base_xp_reward (the Base XP earned from completing the route)
// - xpRequired corresponds to ApiRoute.xp_required (XP needed to unlock the route)

export interface Route {
  id: string;
  name: string;
  type: "hiking" | "running" | "cycling";
  difficulty: "easy" | "medium" | "hard" | "expert";
  distance: number; // in km
  elevation: number; // in meters
  duration: number; // in minutes
  location: string;
  description: string;
  imageUrl: string;
  xpReward: number; // Base XP earned from completing this route (maps to ApiRoute.base_xp_reward)
  rating: number;
  completions: number;
  tags: string[];
  isLocked?: boolean;
  xpRequired?: number; // XP needed to unlock this route (maps to ApiRoute.xp_required)
  breakpoints: Breakpoint[];
  prologue?: string;
  epilogue?: string;
}

export interface Breakpoint {
  id: string;
  name: string;
  distance: number; // km from start
  type: "story" | "quest" | "checkpoint";
  content?: string;
  quest?: MiniQuest;
}

export interface MiniQuest {
  id: string;
  title: string;
  description: string;
  type: "photo" | "quiz" | "observation";
  xpReward: number;
  choices?: string[];
  correctAnswer?: number;
}

export interface UserProfile {
  id: string;
  name: string;
  level: number;
  xp: number;
  xpToNextLevel: number;
  explorerType: string;
  fitnessLevel: "beginner" | "intermediate" | "advanced" | "expert";
  preferredTypes: ("hiking" | "running" | "cycling")[];
  narrativeStyle: string;
  completedRoutes: string[];
  achievements: Achievement[];
  difficultyBias: number;
  distanceBias: number;
  souvenirs: DigitalSouvenir[]; // Added souvenirs array
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlockedAt: Date;
}

export interface DigitalSouvenir {
  id: string;
  routeId: string;
  routeName: string;
  location: string;
  completedAt: Date;
  xpGained: number;
  badgesEarned: string[];
  imageUrl: string;
  difficulty: string;
  distance: number;
}

export const mockRoutes: Route[] = [
  {
    id: "1",
    name: "Schwarzwald Forest Trail",
    type: "hiking",
    difficulty: "medium",
    distance: 8.5,
    elevation: 420,
    duration: 180,
    location: "Black Forest, Germany",
    description:
      "A mystical journey through ancient pine forests with stunning valley views",
    imageUrl: "/black-forest-hiking-trail-misty-morning.jpg",
    xpReward: 250,
    rating: 4.7,
    completions: 342,
    tags: ["forest", "scenic", "moderate"],
    prologue: `The morning mist hangs heavy over the ancient pines of the Schwarzwald. Legends speak of travelers who walked these paths centuries ago, seeking wisdom in the heart of the forest.\n\nYou stand at the threshold of a journey that will test not just your endurance, but your connection to the natural world. The forest beckons, its secrets waiting to be discovered by those brave enough to venture deep into its emerald embrace.\n\nYour quest begins now, adventurer. May the old spirits of the forest guide your steps.`,
    epilogue: `As you emerge from the forest's embrace, the afternoon sun feels warmer than before. The journey through the Schwarzwald has transformed you in ways both visible and invisible.\n\nYou carry with you not just memories, but a deeper understanding of nature's quiet wisdom. The forest has shared its secrets, and you have proven yourself worthy.\n\nThough this particular trail ends here, you know the forest will always welcome you back. Until next time, wanderer.`,
    breakpoints: [
      {
        id: "bp1",
        name: "Forest Entrance",
        distance: 0,
        type: "story",
        content:
          "The towering pines create a natural cathedral around you. Ancient moss covers the stones beneath your feet, and somewhere in the distance, you hear the song of a hidden stream. The air is cool and filled with the scent of pine needles and earth.",
      },
      {
        id: "bp2",
        name: "Hidden Waterfall",
        distance: 3.2,
        type: "quest",
        content:
          "The sound of rushing water grows louder as you round a bend in the trail. Before you, a stunning waterfall cascades down moss-covered rocks into a crystal-clear pool. Sunlight filters through the canopy above, creating dancing patterns of light on the water.",
        quest: {
          id: "q1",
          title: "Nature Observer",
          description:
            "Capture the beauty of the waterfall from three different angles",
          type: "photo",
          xpReward: 50,
        },
      },
      {
        id: "bp3",
        name: "Summit Ridge",
        distance: 6.5,
        type: "story",
        content:
          "You reach a clearing on the ridge, and the view takes your breath away. The entire Black Forest spreads out before you, a sea of green stretching to the horizon. This is why you came. This moment of perfect stillness, where earth meets sky.",
      },
      {
        id: "bp4",
        name: "Trail End",
        distance: 8.5,
        type: "checkpoint",
        content:
          "The trail gently descends back toward civilization. Your legs are tired but your spirit soars. You have completed the journey through one of Germany's most mystical forests.",
      },
    ],
  },
  {
    id: "2",
    name: "Munich City Explorer",
    type: "hiking",
    difficulty: "easy",
    distance: 5.2,
    elevation: 45,
    duration: 120,
    location: "Munich, Germany",
    description:
      "Discover hidden gems and historic landmarks in Bavaria capital",
    imageUrl: "/munich-city-center-marienplatz.jpg",
    xpReward: 150,
    rating: 4.5,
    completions: 589,
    tags: ["urban", "culture", "easy"],
    prologue: `Munich, the heart of Bavaria, pulses with history and culture. From medieval towers to baroque palaces, from beer halls to art galleries, this city is a treasure trove waiting to be discovered.\n\nYour urban adventure begins at Marienplatz, where centuries of stories echo through the cobblestones. Today, you\'ll walk in the footsteps of kings and commoners, discovering the hidden gems that make Munich truly special.`,
    epilogue: `As your journey through Munich concludes, you realize the city has revealed just a fraction of its secrets. Each street corner holds another story, each building another piece of history.\n\nYou\'ve experienced the essence of Bavarian culture, but Munich is a city that rewards those who return. Until your next adventure in the Bavarian capital!`,
    breakpoints: [
      {
        id: "bp1",
        name: "Marienplatz",
        distance: 0,
        type: "story",
        content:
          "The New Town Hall towers above you, its neo-Gothic spires reaching toward the sky. The famous Glockenspiel will soon perform its mechanical dance. Tourists and locals alike gather in this square, the beating heart of Munich.",
      },
      {
        id: "bp2",
        name: "English Garden",
        distance: 2.8,
        type: "quest",
        content:
          "You arrive at the English Garden, one of the world's largest urban parks. Surfers ride the Eisbach wave, joggers pass by, and locals relax on the grass. This oasis in the middle of the city perfectly captures Munich's love of nature.",
        quest: {
          id: "q2",
          title: "Local Culture Quiz",
          description: "What year was the Hofbräuhaus founded?",
          type: "quiz",
          xpReward: 30,
          choices: ["1589", "1607", "1664", "1710"],
          correctAnswer: 0,
        },
      },
      {
        id: "bp3",
        name: "River Isar",
        distance: 5.2,
        type: "story",
        content:
          "The Isar River flows peacefully through the city, its turquoise waters a reminder of the Alps not far away. Locals sunbathe on the banks, and you understand why Munich is considered one of the most livable cities in the world.",
      },
    ],
  },
  {
    id: "3",
    name: "Alpine Summit Challenge",
    type: "hiking",
    difficulty: "expert",
    distance: 14.8,
    elevation: 1250,
    duration: 420,
    location: "Bavarian Alps, Germany",
    description:
      "Conquer towering peaks and experience breathtaking alpine vistas",
    imageUrl: "/bavarian-alps-mountain-summit-sunrise.jpg",
    xpReward: 500,
    rating: 4.9,
    completions: 87,
    tags: ["mountain", "challenging", "epic"],
    isLocked: true,
    xpRequired: 1000,
    breakpoints: [
      {
        id: "bp1",
        name: "Base Camp",
        distance: 0,
        type: "story",
      },
      {
        id: "bp2",
        name: "Ridge Ascent",
        distance: 5.5,
        type: "quest",
        quest: {
          id: "q3",
          title: "Weather Check",
          description: "Identify the cloud formation above",
          type: "quiz",
          xpReward: 75,
          choices: ["Cumulus", "Cirrus", "Stratus", "Nimbus"],
          correctAnswer: 1,
        },
      },
      {
        id: "bp3",
        name: "Summit",
        distance: 14.8,
        type: "checkpoint",
      },
    ],
  },
  {
    id: "4",
    name: "Rhine River Run",
    type: "running",
    difficulty: "medium",
    distance: 10.3,
    elevation: 180,
    duration: 75,
    location: "Rhine Valley, Germany",
    description:
      "A scenic riverside run through vineyards and medieval castles",
    imageUrl: "/rhine-river-valley-vineyards-castle.jpg",
    xpReward: 280,
    rating: 4.6,
    completions: 234,
    tags: ["river", "scenic", "moderate"],
    breakpoints: [
      {
        id: "bp1",
        name: "Starting Point",
        distance: 0,
        type: "story",
      },
      {
        id: "bp2",
        name: "Castle View",
        distance: 5.0,
        type: "checkpoint",
      },
      {
        id: "bp3",
        name: "Finish Line",
        distance: 10.3,
        type: "story",
      },
    ],
  },
  {
    id: "5",
    name: "Berlin Wall Heritage Walk",
    type: "hiking",
    difficulty: "easy",
    distance: 6.5,
    elevation: 25,
    duration: 150,
    location: "Berlin, Germany",
    description: "Follow the path of history along the former Berlin Wall",
    imageUrl: "/berlin-wall-memorial-east-side-gallery.jpg",
    xpReward: 180,
    rating: 4.8,
    completions: 456,
    tags: ["history", "urban", "educational"],
    breakpoints: [
      {
        id: "bp1",
        name: "Brandenburg Gate",
        distance: 0,
        type: "story",
      },
      {
        id: "bp2",
        name: "Checkpoint Charlie",
        distance: 3.2,
        type: "quest",
        quest: {
          id: "q4",
          title: "History Detective",
          description: "When did the Berlin Wall fall?",
          type: "quiz",
          xpReward: 40,
          choices: ["1987", "1989", "1991", "1990"],
          correctAnswer: 1,
        },
      },
      {
        id: "bp3",
        name: "East Side Gallery",
        distance: 6.5,
        type: "checkpoint",
      },
    ],
  },
  {
    id: "6",
    name: "Saxon Switzerland Trek",
    type: "hiking",
    difficulty: "hard",
    distance: 12.4,
    elevation: 680,
    duration: 300,
    location: "Saxon Switzerland, Germany",
    description: "Explore dramatic sandstone formations and rock pinnacles",
    imageUrl: "/saxon-switzerland-bastei-bridge-rock-formation.jpg",
    xpReward: 380,
    rating: 4.8,
    completions: 156,
    tags: ["rocks", "scenic", "challenging"],
    isLocked: true,
    xpRequired: 500,
    breakpoints: [
      {
        id: "bp1",
        name: "Trail Head",
        distance: 0,
        type: "story",
      },
      {
        id: "bp2",
        name: "Bastei Bridge",
        distance: 6.2,
        type: "quest",
        quest: {
          id: "q5",
          title: "Rock Formation Study",
          description: "Photograph the unique sandstone pillars",
          type: "photo",
          xpReward: 60,
        },
      },
      {
        id: "bp3",
        name: "Return Path",
        distance: 12.4,
        type: "checkpoint",
      },
    ],
  },
];

export const defaultUserProfile: UserProfile = {
  id: "user-1",
  name: "Explorer",
  level: 1,
  xp: 0,
  xpToNextLevel: 300,
  explorerType: "Unknown",
  fitnessLevel: "beginner",
  preferredTypes: [],
  narrativeStyle: "adventure",
  completedRoutes: [],
  achievements: [],
  difficultyBias: 0,
  distanceBias: 0,
  souvenirs: [], // Added empty souvenirs array
};

export const questionnaireQuestions = [
  {
    id: "fitness",
    question: "How would you describe your current fitness level?",
    type: "single",
    options: [
      { value: "beginner", label: "Beginner - Just starting out", icon: "🌱" },
      {
        value: "intermediate",
        label: "Intermediate - Regular activity",
        icon: "🏃",
      },
      { value: "advanced", label: "Advanced - Very active", icon: "💪" },
    ],
  },
  {
    id: "type",
    question: "What type of adventures call to you?",
    type: "multiple",
    options: [
      { value: "history-culture", label: "History & Culture", icon: "🏛️" },
      { value: "natural-scenery", label: "Natural Scenery", icon: "🌲" },
      { value: "family-fun", label: "Family Fun", icon: "👨‍👩‍👧‍👦" },
    ],
  },
  {
    id: "narrative",
    question: "What kind of story draws you in?",
    type: "single",
    options: [
      { value: "adventure", label: "Epic Adventures", icon: "⚔️" },
      { value: "mystery", label: "Mysterious Discoveries", icon: "🔍" },
      { value: "playful", label: "Playful adventure", icon: "🎮" },
    ],
  },
];
