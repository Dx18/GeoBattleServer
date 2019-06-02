from math import ceil, sqrt
from contextlib import closing
import sys


def rewrite(d):
    l = []
    for i in d.keys():
        l.append({})
        l[-1]["hangarId"] = i
        l[-1]["health"] = d[i]
    return l


# Time point where parameters of sector's health and units' healths are changing
class TimePoint:
    def __init__(self, time, sectorHealth):
        self.time = time
        self.planeGroupsHealth = {}
        self.sectorHealth = sectorHealth

    def addPlaneGroupHealth(self, hangarId, health):
        self.planeGroupsHealth[hangarId] = health

    def __str__(self):
        return "{{\"time\": {}, \"planeGroupsHealth\": {}, \"sectorHealth\": {}}}".format(
            self.time,
            rewrite(self.planeGroupsHealth),
            self.sectorHealth
        )

    @staticmethod
    def create(time, sectorHealth, planes, hangars):
        result = TimePoint(time, sectorHealth)
        for hangarId in planes:
            result.addPlaneGroupHealth(hangarId, planes[hangarId])
        for hangarId in hangars:
            if not hangarId in result.planeGroupsHealth:
                result.addPlaneGroupHealth(hangarId, hangars[hangarId].planeCount * PLANE_HEALTH())
        return result

    @staticmethod
    def createFromTimePoint(timePoint):
        result = TimePoint(timePoint.time, timePoint.sectorHealth)
        result.planeGroupsHealth = timePoint.planeGroupsHealth
        return result

# Info about hangar


class HangarInfo:
    def __init__(self, x, y, planeCount):
        self.x = x
        self.y = y
        self.planeCount = planeCount

    def __str__(self):
        return "{{ x = {}, y = {}, planeCount = {} }}".format(self.x, self.y, self.planeCount)

# Info about sector


class SectorInfo:
    def __init__(self, id, x, y, turretCount, health):
        self.id = id
        self.x = x
        self.y = y
        self.turretCount = turretCount
        self.health = health

    def __str__(self):
        return "{{ id = {}, x = {}, y = {}, turretCount = {}, health = {} }}".format(
            self.id, self.x, self.y, self.turretCount, self.health
        )

# Info about unit moving


class UnitGroupMovingInfo:
    def __init__(self, hangarId, arriveTime, arriveX, arriveY, returnTime):
        self.hangarId = hangarId
        self.arriveTime = arriveTime
        self.arriveX = arriveX
        self.arriveY = arriveY
        self.returnTime = returnTime

    def __str__(self):
        return "{{ \"hangarId\": {}, \"arriveTime\": {}, \"arriveX\": {}, \"arriveY\": {}, \"returnTime\": {}}}".format(
            self.hangarId,
            self.arriveTime,
            self.arriveX,
            self.arriveY,
            self.returnTime
        )

# Full attack event scenario


class AttackScript:
    def __init__(self, attackerId, victimId, sectorId, unitGroupMoving, timePoints):
        self.attackerId = attackerId
        self.victimId = victimId
        self.sectorId = sectorId
        self.unitGroupMoving = unitGroupMoving
        self.timePoints = timePoints

    def __str__(self):
        return "{{\n    \"attackerId\": {},\n    \"victimId\": {},\n    \"sectorId\": {},\n    \"unitGroupMoving\": [\n{}\n    ],\n    \"timePoints\": [\n{}\n    ]\n}}".format(
            self.attackerId,
            self.victimId,
            self.sectorId,
            ",\n".join(map(lambda x: "        {}".format(str(x)), self.unitGroupMoving)),
            ",\n".join(map(lambda x: "        {}".format(str(x)), self.timePoints))
        )

# const


def PLANE_HEALTH():
    return 50

# var


def TURRET_DAMAGE(id, db):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:
                cur.execute("SELECT idPlayer FROM Sectors WHERE id={};".format(id))
                idPlayer = cur.fetchall()[0][0]
                cur.execute("SELECT levelT FROM Players WHERE id={};".format(idPlayer))
                return 5 + cur.fetchall()[0][0]
    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    return 5


def PLANE_DAMAGE(id, db):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:
                cur.execute("SELECT idSector FROM Buildings WHERE id={};".format(id))
                idSector = cur.fetchall()[0][0]
                cur.execute("SELECT idPlayer FROM Sectors WHERE id={};".format(idSector))
                idPlayer = cur.fetchall()[0][0]
                cur.execute("SELECT levelP FROM Players WHERE id={};".format(idPlayer))
                return 10 + cur.fetchall()[0][0]
    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    return 5

# const


def PLANE_SPEED():
    return 5

# Returns health of weakest plane


def calcWeakest(health):
    result = health % PLANE_HEALTH()
    if result == 0:
        return PLANE_HEALTH()
    return result

# Returns distance between two points


def dist(x1, y1, x2, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# Simulates single battle
# Params:
# - planes (dict<int ("hangarId"), double ("health")>) - healths of planes
# - hangars (dict<int ("hangarId"), HangarInfo ("hangar")>) - hangars
# - sector (SectorInfo) - info about sector
# - startTime (double) - start time
# - maxTime (double) - time of max time point


def fighting_single(planes, hangars, sector, startTime, maxTime, db):
    result = []

    totalTime = startTime

    planeCount = 0
    planeGroupCount = 0
    for hangarId in planes:
        planeCount += ceil(planes[hangarId] / PLANE_HEALTH())
        if planes[hangarId] > 0:
            planeGroupCount += 1

    while totalTime < maxTime and sector.health > 0 and planeCount > 0:
        turretDamagePerPlane = sector.turretCount * TURRET_DAMAGE(sector.id, db) / planeGroupCount
        weakestPlaneHealth = min(map(calcWeakest, planes.values()))
        time1 = weakestPlaneHealth / turretDamagePerPlane if turretDamagePerPlane > 0 else float("inf")

        planeDamage = PLANE_DAMAGE(list(hangars.keys())[-1], db) * planeCount
        time2 = sector.health / planeDamage

        time3 = maxTime - totalTime

        time = min(time1, time2, time3)
        totalTime += time

        sector.health -= time * planeDamage

        planeCount = 0
        planeGroupCount = 0
        for hangarId in planes.keys():
            if planes[hangarId] > 0:
                planes[hangarId] -= time * turretDamagePerPlane
            if planes[hangarId] > 0:
                planeCount += ceil(planes[hangarId] / PLANE_HEALTH())
                planeGroupCount += 1

        newTimePoint = TimePoint.create(totalTime, sector.health, planes, hangars)

        result.append(newTimePoint)

    return result

# Simulates battle
# Params:
# - attackerId (int) - ID of attacker (person who owns planes)
# - victimId (int) - ID of victim (person who owns sector)
# - hangars (dict<int ("hangarId"), HangarInfo ("hangar")>) - info about all hangars
# - sector (SectorInfo) - info about sector


def fighting(attackerId, victimId, hangars, sector, baseTime, db):
    # Arrive times for plane groups from hangars
    # Type: [(int ("hangarId"), double ("arriveTime"))]
    arriveTimes = [(
        hangarId,
        dist(sector.x, sector.y, hangars[hangarId].x, hangars[hangarId].y) / PLANE_SPEED()
    ) for hangarId in hangars]

    arriveTimes.append((-1, float("inf")))
    arriveTimes.sort(key=(lambda arriveTime: arriveTime[1]))

    # Time points
    # Type: [TimePoint]
    timePoints = []

    # Planes' health
    # Type: dict<int ("hangarId"), double ("health")>
    planes = {}

    # Adding initial time point
    timePoints.append(TimePoint.create(0, sector.health, planes, hangars))

    reachedCount = 0

    # For each arrive time...
    for i in range(len(arriveTimes) - 1):
        # Adding plane group
        hangarId, arriveTime = arriveTimes[i]
        planes[hangarId] = hangars[hangarId].planeCount * PLANE_HEALTH()

        if len(timePoints) == 0 or timePoints[-1].time != arriveTime:
            timePoints.append(TimePoint.create(arriveTime, sector.health, planes, hangars))

        # New time points
        # Type: [TimePoint]
        newTimePoints = fighting_single(
            planes, hangars, sector,
            arriveTimes[i][1], arriveTimes[i + 1][1],
            db
        )

        if len(newTimePoints) == 0:
            continue

        # Last time point
        # Type: TimePoint
        lastTimePoint = newTimePoints[-1]

        # Updating planes and sector
        for hangarId in lastTimePoint.planeGroupsHealth:
            if hangarId in planes:
                planes[hangarId] = lastTimePoint.planeGroupsHealth[hangarId]
        sector.health = lastTimePoint.sectorHealth

        # Adding new time points
        timePoints.extend(newTimePoints)

        reachedCount += 1
        if sector.health == 0:
            break

    # Adding unit group moving
    unitGroupMoving = []
    for i in range(reachedCount):
        if timePoints[-1].planeGroupsHealth[arriveTimes[i][0]] <= 0:
            returnTime = timePoints[-1].time + 1
        else:
            returnTime = timePoints[-1].time + arriveTimes[i][1]
        unitGroupMoving.append(UnitGroupMovingInfo(
            arriveTimes[i][0], arriveTimes[i][1], sector.x, sector.y,
            returnTime
        ))
    for i in range(reachedCount, len(arriveTimes) - 1):
        hangarX = hangars[arriveTimes[i][0]].x
        hangarY = hangars[arriveTimes[i][0]].y
        unitGroupMoving.append(UnitGroupMovingInfo(
            arriveTimes[i][0],
            timePoints[-1].time,
            hangarX + (sector.x - hangarX) * timePoints[-1].time / arriveTimes[i][1],
            hangarY + (sector.y - hangarY) * timePoints[-1].time / arriveTimes[i][1],
            timePoints[-1].time * 2
        ))

    timePoints.append(TimePoint.createFromTimePoint(timePoints[-1]))
    if timePoints[-1].sectorHealth == 0 and max(timePoints[-1].planeGroupsHealth.values()) > 0:
        timePoints[-1].time = max(map(lambda info: info.returnTime, unitGroupMoving))
    else:
        timePoints[-1].time = timePoints[-2].time + 1

    for timePoint in timePoints:
        timePoint.time += baseTime
    for hangar in range(len(unitGroupMoving)):
        unitGroupMoving[hangar].arriveTime += baseTime
        unitGroupMoving[hangar].returnTime += baseTime

    return AttackScript(attackerId, victimId, sector.id, unitGroupMoving, timePoints)
