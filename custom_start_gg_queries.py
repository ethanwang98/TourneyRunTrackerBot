SHOW_SETS_WITH_SEED_QUERY = """query EventSets($eventId: ID!, $page: Int!) {
  event(id: $eventId) {
    tournament {
      id
      name
    }
    name
    state
    sets(page: $page, perPage: 18, sortType: STANDARD) {
      nodes {
        fullRoundText
        games {
          winnerId
          selections {
            selectionValue
            entrant {
              id
            }
          }
        }
        id
        slots {
          standing {
            id
            placement
            stats {
              score {
                value
              }
            }
          }
          entrant {
            id
            name
            initialSeedNum
            participants {
              entrants {
                id
              }
              player {
                id
                gamerTag
                
              }
            }
          }
        }
        phaseGroup {
          id
          phase {
            name
          }
        }
      }
    }
  }
}
"""

SHOW_EVENT_METADATA = """query ($tourneySlug: String!) {
  tournament(slug: $tourneySlug) {
    name
    events {
      id
      slug
      name
      state
    }
  }
}
"""
