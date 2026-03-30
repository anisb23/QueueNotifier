QueueNotifierDB = QueueNotifierDB or {}

local frame = CreateFrame("Frame")
frame:RegisterEvent("PLAYER_LOGIN")

frame:SetScript("OnEvent", function(self, event)
    if event == "PLAYER_LOGIN" then
        print("|cff00ccff[QueueNotifier]|r Loaded. Waiting for queue pop...")
    end
end)

hooksecurefunc("PVPReadyDialog_Display", function(_, battlefieldId)
    local status, mapName, teamSize, registeredMatch, suspendedQueue, queueType, gameType, role, asGroup, shortDescription, longDescription, isSoloQueue = GetBattlefieldStatus(battlefieldId)

    print("|cffff9900[QueueNotifier DEBUG]|r PVPReadyDialog_Display fired!")
    print("|cffff9900[QueueNotifier DEBUG]|r battlefieldId=" .. tostring(battlefieldId))
    print("|cffff9900[QueueNotifier DEBUG]|r status=" .. tostring(status))
    print("|cffff9900[QueueNotifier DEBUG]|r mapName=" .. tostring(mapName))
    print("|cffff9900[QueueNotifier DEBUG]|r teamSize=" .. tostring(teamSize))
    print("|cffff9900[QueueNotifier DEBUG]|r queueType=" .. tostring(queueType))
    print("|cffff9900[QueueNotifier DEBUG]|r gameType=" .. tostring(gameType))
    print("|cffff9900[QueueNotifier DEBUG]|r isSoloQueue=" .. tostring(isSoloQueue))

    QueueNotifierDB.lastPop = time()
    QueueNotifierDB.status = "popped"
    QueueNotifierDB.debug = {
        battlefieldId = battlefieldId,
        status = status,
        mapName = mapName,
        teamSize = teamSize,
        queueType = queueType,
        gameType = gameType,
        isSoloQueue = isSoloQueue,
    }
    print("|cff00ff00[QueueNotifier]|r Queue popped! Notification sent.")
end)
