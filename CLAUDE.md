# 로블록스 애니 가챠 배틀 게임 - 프로젝트 지침

이 프로젝트는 로블록스 스튜디오에서 Luau로 개발하는 가챠+배틀 게임입니다.
코드를 생성할 때 아래 규칙을 반드시 따르세요.

## 언어 및 환경

- 언어: Luau (로블록스 전용 Lua)
- 엔진: Roblox Studio
- 서버-클라이언트 구조: Script(서버), LocalScript(클라이언트), ModuleScript(공유)

## 폴더 구조

```
ServerScriptService/
  GameManager (Script)        -- 플레이어 접속 처리, 초기화
  DataManager (Script)        -- DataStore 저장/로드
  RouletteSystem (Script)     -- 룰렛 확률 계산, 캐릭터 지급
  BattleSystem (Script)       -- 턴제 전투 로직
  TowerSystem (Script)        -- 타워 몹 스폰, 스테이지 관리
  CombineSystem (Script)      -- 조합소 로직
  UpgradeSystem (Script)      -- 강화소 로직
  CurrencySystem (Script)     -- 재화 관리
  DailyReward (Script)        -- 일일보상 로직
  PVPSystem (Script)          -- PVP 매칭, 결과 처리
  RebirthSystem (Script)      -- 환생 로직

ReplicatedStorage/
  Remotes/ (Folder)           -- RemoteEvent 모음
    SpinRoulette
    StartBattle
    BattleResult
    RequestUpgrade
    RequestCombine
    RequestRebirth
    ClaimDailyReward
    StartPVP
    PVPResult
    EnterTower
    TowerResult
    CombineResult
    UpgradeResult
    UpdateCurrency
    UpdateUI
    BuyUpgrade
  Modules/ (Folder)           -- 공유 ModuleScript
    CharacterData             -- 캐릭터 스탯/등급 데이터
    ItemData                  -- 자원/아이템 데이터
    Config                    -- 전체 게임 설정값
  Characters/ (Folder)        -- 캐릭터 모델 저장

StarterGui/
  MainHUD (ScreenGui)         -- 재화 표시
  RouletteGui (ScreenGui)     -- 룰렛 UI
  InventoryGui (ScreenGui)    -- 캐릭터 목록 UI
  BattleGui (ScreenGui)       -- 전투 UI
  ShopGui (ScreenGui)         -- 상점 UI
  DailyRewardGui (ScreenGui)  -- 일일보상 팝업
  CutsceneGui (ScreenGui)     -- 컷신 연출 UI

StarterPlayerScripts/
  UIController (LocalScript)  -- 모든 UI 이벤트 처리

Workspace/
  Map/
    Base                      -- 중앙 기지
    Tower                     -- 타워 건물
    Arena                     -- PVP 결투장
    SemShop                   -- 조합소 (NPC: Sem)
    TomShop                   -- 강화소 (NPC: Tom)
    Teleporters               -- 텔레포트 위치들
```

## 보안 규칙

- 재화 변경, 확률 계산, 강화/조합 결과는 반드시 서버(Script)에서 처리
- 클라이언트(LocalScript)는 UI 표시와 RemoteEvent 발사만 담당
- 서버에서 항상 플레이어 데이터를 검증한 후 처리 (치트 방지)
- RemoteEvent 핸들러에서 인자 타입과 범위를 검증

## 플레이어 데이터 구조 (DataStore)

DataManager가 관리하는 플레이어별 저장 데이터:

```lua
{
    Gold = 100,              -- 골드 (기본 재화)
    EnhanceCoin = 0,         -- 강화코인 (타워 보상)
    Characters = {},         -- 보유 캐릭터 목록 [{Name, Rarity, UpgradeLevel}]
    Inventory = {},          -- 보유 자원 목록 {["Shadow Crystal"] = 3, ...}
    DailyRewardDay = 0,      -- 일일보상 현재 일차
    LastLoginTime = 0,       -- 마지막 접속 시간 (os.time)
    RebirthCount = 0,        -- 환생 횟수
    DiceLevel = 1,           -- 주사위 레벨 (룰렛 확률 보너스)
    SpinSpeed = 1,           -- 룰렛 속도 레벨
    TowerFloor = 0,          -- 타워 최고 도달 층
}
```

## 캐릭터 데이터 구조 (CharacterData 모듈)

```lua
{
    Name = "전사",
    Rarity = "Common",       -- Common/Uncommon/Rare/Epic/Legendary/Mythic
    HP = 400,
    ATK = 80,
    DEF = 50,
    SPD = 60,                -- 선공 판정용
    Skill = "강타",
    SkillDamage = 120,
    ModelName = "Warrior",   -- Characters 폴더의 모델 이름과 일치해야 함
    HasCutscene = false,     -- Mythic만 true
    IsVariant = false,       -- 변이체 여부
    VariantOf = nil,         -- 원본 캐릭터 이름 (변이체만)
    CombineRecipe = nil,     -- 조합 레시피 (nil이면 조합 불가)
}
```

## 등급 시스템

| 등급 | 확률 | HP 범위 | ATK 범위 | DEF 범위 |
|------|------|---------|----------|----------|
| Common | 1/2 | 300~500 | 50~100 | 30~60 |
| Uncommon | 1/5 | 500~800 | 100~200 | 60~120 |
| Rare | 1/20 | 800~1200 | 200~350 | 120~200 |
| Epic | 1/100 | 1200~1800 | 350~500 | 200~300 |
| Legendary | 1/500 | 1800~2500 | 500~750 | 300~450 |
| Mythic | 1/5000 | 2500~4000 | 750~1200 | 450~700 |

등급 색상: Common=회색, Uncommon=초록, Rare=파랑, Epic=보라, Legendary=금색, Mythic=빨강

## 전투 공식

```
데미지 = 공격자ATK - (방어자DEF * 0.5)
최소 데미지 = 1
선공 판정 = SPD가 높은 쪽
스킬 발동 = 매 5턴마다 (SkillDamage 추가 적용)
```

## 재화 종류

- **골드**: 기본 재화. 전투 승리, 일일보상으로 획득. 룰렛/상점/조합에서 소모
- **강화코인**: 타워 보상으로 획득. 강화소에서 소모
- **자원**: 타워 층별 드롭. 조합소에서 소모 (Shadow Crystal, Light Fragment, Dark Essence, Dragon Scale, Divine Tear)

## 코딩 컨벤션

- 서버 스크립트 간 통신: ModuleScript를 require()로 공유
- 클라이언트-서버 통신: RemoteEvent만 사용 (RemoteFunction 지양)
- 변수 네이밍: camelCase (지역변수), PascalCase (서비스, 모듈)
- print() 디버그 메시지에 스크립트 이름 접두사: `print("[DataManager] 데이터 로드 완료")`
- task.wait() 사용 (wait() 대신)
- 에러 처리: pcall로 DataStore 호출 감싸기

## 환생 공식

```
환생 비용 = 10000 * (1 + RebirthCount * 0.5) 골드
전투 보상 배율 = 1 + (RebirthCount * 0.5)
룰렛 확률 보너스 = 1 + (RebirthCount * 0.1)
환생 시 리셋: Gold, Characters, DiceLevel
환생 시 유지: RebirthCount, EnhanceCoin
```

## 강화 공식

```
강화 비용 = 레벨 * 3 강화코인 + 레벨 * 200 골드
스탯 증가 = 레벨당 +5%
성공률: 레벨 1~5 = 90%, 레벨 6~8 = 60%, 레벨 9~10 = 30%
실패 시: 재료만 소모, 레벨 유지
최대 강화 레벨: 10
```

## 조합 공식

```
기본 성공률: 70%
실패 시: 재료만 소모, 캐릭터 유지
성공 시: 기존 캐릭터 제거 + 변이체 캐릭터 추가
```
