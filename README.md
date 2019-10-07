# EZworkEra
Utility For using UpdateEra(Not Mine) - Translated Eramaker base game's update tool

## readme ver 2.0 2019.08.19
이 파일은 readme 텍스트 파일로, 현재 존재하는 툴의 기능을 설명하고 있습니다.

# 개요
기본적으로 이 툴의 목적은 이미 손/기계번역된 파일이 존재하는 era를, 이후 원본 era의 업데이트시 srs를 활용해 상대적으로 원활하게
통합할 수 있도록 도움을 주는 목적으로 제작되고 있습니다.
이 툴은 ver 2.0 현재 eraTW의 파일구조를 참고하여 만들어졌습니다. 타 era에서의 구동을 보장할 수 없습니다.
이 툴은 ver 2.0 현재 python 3.7.4를 기반으로 작성되고 있습니다. C 계열이던 Java 계열이던 다른 언어는 아예 만질 줄 모릅니다.
현재 개발/수정중인 코드, 그리고 이전 릴리즈 코드는 소스코드 디렉토리 내에 동봉되어 있습니다.
UpdateEra의 구조는 전혀 모르지만, srs의 사용에 조금이나마 도움이 될 수 있도록 구성하고자 합니다.
srs의 구조에 대해 아시는 분의 많은 도움 부탁드립니다.
현재 미천한 프로그래밍 실력으로 최대한 노력하고 있사오니, 능력자분의 많은 도움 부탁드립니다.
	
# trans_csv_to_srs.exe
1. extractj/ 디렉토리와 extractK/ 디렉토리 내부의 CSV 파일의 특정 변수를 필터링하여 TXT 자료화 및 srs 양식에 맞게 정리하는 툴입니다.
  * 되도록 원본과 번역본은 csv 파일의 내용물이 변하지 않은 상태인 것(그러니까 되도록 같은버전)만 넣어주세요. 이후 수작업할 분량이 늘어납니다.
  * ver 2.0 현재 UTF-8 인코딩만을 지원하기에 원본 csv 파일의 경우 shift-jif 인코딩인 경우가 많아 인코딩 변환을 미리 하셔야 합니다.
  * ver 2.0 현재 각 extract 디렉토리 내 하위폴더의 검색은 지원하지 않아, 각 파일을 바로 아래에 집어넣으셔야 합니다.
  * 원본과 번역본 csv 파일을 디렉토리 안에 넣으실 때에는 파일명의 철자 순서를 고려해서 넣어주세요. 현재 파일명의 철자 순서가 뒤죽박죽이라면 결과물도 뒤죽박죽으로 나옵니다.
  * chara 내의 csv 파일 구조를 기반으로 만들었기에 타 csv 파일에서는 문제가 발생할 수 있습니다.
  * ver 2.0 현재 숫자형 자료와 csv 양식을 오염시킬 수 있는 쉼표 기호, 그리고 파일군 내에서 중복되는 문자열은 필터링됩니다.
2. 위 툴의 소스코드는 이전 두 툴의 소스코드를 합병한 결과물입니다. 따라서 이전 툴의 대부분의 기능(번호 관련 기능 제외)을 사용할 수 있습니다.
3. CSVfnclist.csv내 목록을 활용해 특정 변수를 식별합니다. 이를 통해 입력한 변수명과 csv 파일 내 변수명의 언어가 다르더라도(ex. NAME과 名前) 이를 식별해 추출합니다.
4. extractJ/의 지정 변수 필터 결과물은 extractJ.txt, extractK/의 지정 필터 결과물은 extractK.txt에 저장됩니다.
5. csv 내 자료 추출 이후 추가로 진행할수도, 각각의 텍스트파일만 남긴 체 'end'를 눌러 끝낼수도 있습니다.
  * 해당 단계에서 이미 각 결과물 txt는 출력이 완료된 상태로, 이후 단계는 엔터를 눌러 추가 진행하기 '직전' 각 텍스트파일 결과물의 내용을 불러와 작성됩니다.
  * 따라서 추가 진행 이전에 1.의 유의사항을 참고하셔서 각 결과물 txt가 양쪽의 줄 정렬상태가 맞는지, 이상한 내용이 끼어있지는 않은지 확인하시고 미리 수작업으로 처리해주세요.
6. 추가 진행시, srs 파일과 두 필터 결과물의 합본인 txt파일이 작성됩니다.
7. srs 파일 양식 작성시, 최초작성의 경우 기본 양식(TRIM과 SORT)을 쓰도록 설정할 수 있습니다.
8. srs 파일 양식 작성시 해당 결과물의 첫 줄은 ;이하 (입력한 변수명) 이라는 주석이 달립니다. 분류할 때 참고하세요.
9. txt 파일의 경우 <원본 결과물><줄바꿈><번역 결과물><줄바꿈><줄바꿈>의 형태로 구성됩니다. 차후 버전에서 수정될 수 있습니다.
10. 위 툴은 한 번 구동할 때 이미 폴더 내에 존재하는 추출된 텍스트 파일을 지우고 다시 생성하므로, 한 번 완성된 파일은 따로 보관해주세요.
  * srs 파일은 이어쓰는 방식이기에 이전 결과물이 사라지지는 않지만 srs 파일 내 중복 여부는 판별하지 않으므로 같은 csv를 지속적으로 구동할 경우 중복이 계속 발생하게 됩니다.

# 오류, 개선 등 보고 관련하여
텍마갤 눈팅족으로도 있기는 하지만 참치넷 쪽이 보기 편합니다. 차후 github로의 프로젝트 이식을 고려하고 있습니다. readme 내 누락되거나 현재 적용되지 않는 설명이 있다고 느껴질 경우 바로 보고해주세요.

# 이후 예정(이슈 트레커)
## 우선사항
* 인코딩이 UTF-8이 아니어도 바로 툴의 적용이 가능하도록.
* 타 csv 구조 분석을 통한 지원 강화 및 이를 통한 특정 변수 식별 기능 업데이트
* csv 파일명이 엉망이어도 어느 정도 커버 가능하도록.
* 별개의 두 툴일때의 기능 복구
  * srs 제작 부분, 또는 합체된 결과물 txt까지만 만들 수도 있도록 개선
  * 결과물 파일 내 순서 정렬 여부 식별 가능한 정보 추가
  * 결과물 txt의 빠른 csv화 가능하도록
## 보류
* 타 era와의 호환 개선. 한다면 eraK가 먼저일 것으로 예상됨.
* 검색 디렉토리 내 하위폴더 검색 지원
  * era의 csv 폴더를 바로 넣어도 작동 가능하도록.(타 csv 양식도 적용 가능해야 의미있는 기능)
  * 검색 디렉토리명이나 결과물 텍스트 파일 이름 커스터마이징 지원(만든다면 실행 파일의 하위에서만. 컴퓨터 전체는 허들 높음)
		
# 작성 로그
## ver 1.0
'chara CSV 이름추출', 'CSV 이름 srs 변환 구동'의 설명 작성
readme 파일 작성
## ver 2.0
'chara CSV 이름추출', 'CSV 이름 srs 변환 구동' 설명 및 패키지 파일 제거
  * 해당 툴들의 소스코드는 소스코드 디렉토리 내 보존됨.
'trans_csv_to_srs' 설명 작성
readme 관련 내용 수정 및 개정
## ver 2.1
readme 파일 마크다운 문법에 맞게 가독성 개선

# 개발자 모두발언
## ver 2.1? 2019/10/08
현재 기여자가 프로젝트 관리자인 저밖에 없는 관계로 생각보다 코드 갈아엎기나 모듈 분할 같은 일을 자주 만들고 있습니다. 따라서 만약. 마안약에 기여를 하시고자 할 때에는 되도록 브랜치를 따로 하셔야 나중에 통합할 때 편할 것 같습니다. 어차피 통합도 제가 하니 마음 편하게 가지시고 참여해주시면 감사하겠습니다.
### 현재 모듈 파편화 상황
* Mainstream.py - 다양한 모듈들의 최종 구동지점. 클래스나 함수를 만드실 때에는 이곳 말고 기능별로 나눠진 곳에 만들어주시기 바랍니다.
* Custom 시리즈
  * Custom_Main.py - 여러 상황에서 범용적으로 사용 가능한 클래스의 집합.
  * Custom_CSV.py - CSV 관련 기능 클래스 집합
  * Custom_ERB.py - ERB 관련 기능 클래스 집합
현재 이곳에 표기된 모듈 이외에는 모두 과거 코드이거나 실험용 코드이므로 참고바랍니다. 추가로 릴리즈를 하지 않았다는 점에서 알 수 있듯 원래 있던 기능도 제대로 돌아가지 않는 상황입니다. 컴파일했을때 어떻게 될지가 무섭네요...
