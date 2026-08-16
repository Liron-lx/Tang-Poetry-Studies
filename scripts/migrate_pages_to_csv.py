#!/usr/bin/env python3
"""把 word-association.html / poetry-emotion.html 的内嵌数据替换为 fetch 读取 data/ 权威 CSV。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EMO_LOADER = """        // 权威数据源：data/emotion_scores.csv（100 条，量程 0-10 分）
        var data = [];
        fetch('data/emotion_scores.csv')
          .then(function(resp) { return resp.text(); })
          .then(function(text) {
            var lines = text.trim().split('\\n');
            var headers = lines[0].replace(/^\\uFEFF/, '').split(',');
            data = lines.slice(1).filter(function(l) { return l.trim().length; }).map(function(line) {
              var cols = line.split(',');
              var obj = {};
              headers.forEach(function(h, i) { obj[h] = cols[i]; });
              return obj;
            });
"""

WF_LOADER = """        // 权威数据源：data/word_frequency.csv（283 词全量版）
        let data = [];
        fetch('data/word_frequency.csv')
          .then(resp => resp.text())
          .then(text => {
            const lines = text.trim().split('\\n');
            const headers = lines[0].replace(/^\\uFEFF/, '').split(',');
            data = lines.slice(1).filter(l => l.trim()).map(line => {
              const cols = line.split(',');
              const obj = {};
              headers.forEach((h, i) => obj[h] = cols[i]);
              return obj;
            });
"""


def patch(path, var_pattern, loader, tail_anchor, tail_replacement):
    text = path.read_text(encoding='utf-8')
    new, n = re.subn(var_pattern, lambda _: loader.rstrip('\n'), text, flags=re.S)
    assert n == 1, f'{path.name}: 数据数组替换次数={n}'
    assert tail_anchor in new, f'{path.name}: 找不到尾部锚点'
    new = new.replace(tail_anchor, tail_replacement, 1)
    path.write_text(new, encoding='utf-8')
    print(f'{path.name}: OK')


# word-association.html：var data = [...]（含收尾注释）-> fetch 包裹
patch(
    ROOT / 'word-association.html',
    r'var data = \[.*?\];',
    EMO_LOADER,
    """                }
            }
        });
      </script>""",
    """                }
            }
        });
          });
      </script>""",
)

# poetry-emotion.html：const data = [...] -> fetch 包裹
patch(
    ROOT / 'poetry-emotion.html',
    r'const data = \[.*?\];',
    WF_LOADER,
    """            chart.resize();
        });
    </script>""",
    """            chart.resize();
        });
          });
    </script>""",
)
