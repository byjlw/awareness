import pytest
import json
import yaml
from awareness.utils.search_terms import SearchTermsLoader

@pytest.fixture
def sample_terms():
    return ['term1', 'term2', 'term3']

def test_load_terms_from_txt(tmp_path, sample_terms):
    txt_file = tmp_path / 'terms.txt'
    with open(txt_file, 'w') as f:
        f.write('\n'.join(sample_terms))
    
    loaded_terms = SearchTermsLoader.load_terms(str(txt_file))
    assert loaded_terms == sample_terms

def test_load_terms_from_csv(tmp_path, sample_terms):
    csv_file = tmp_path / 'terms.csv'
    with open(csv_file, 'w') as f:
        f.write('\n'.join(sample_terms))
    
    loaded_terms = SearchTermsLoader.load_terms(str(csv_file))
    assert loaded_terms == sample_terms

def test_load_terms_from_json_list(tmp_path, sample_terms):
    json_file = tmp_path / 'terms.json'
    with open(json_file, 'w') as f:
        json.dump(sample_terms, f)
    
    loaded_terms = SearchTermsLoader.load_terms(str(json_file))
    assert loaded_terms == sample_terms

def test_load_terms_from_json_dict(tmp_path, sample_terms):
    json_file = tmp_path / 'terms.json'
    with open(json_file, 'w') as f:
        json.dump({'terms': sample_terms}, f)
    
    loaded_terms = SearchTermsLoader.load_terms(str(json_file))
    assert loaded_terms == sample_terms

def test_load_terms_from_yaml_list(tmp_path, sample_terms):
    yaml_file = tmp_path / 'terms.yml'
    with open(yaml_file, 'w') as f:
        yaml.dump(sample_terms, f)
    
    loaded_terms = SearchTermsLoader.load_terms(str(yaml_file))
    assert loaded_terms == sample_terms

def test_load_terms_from_yaml_dict(tmp_path, sample_terms):
    yaml_file = tmp_path / 'terms.yml'
    with open(yaml_file, 'w') as f:
        yaml.dump({'terms': sample_terms}, f)
    
    loaded_terms = SearchTermsLoader.load_terms(str(yaml_file))
    assert loaded_terms == sample_terms

def test_load_terms_from_nonexistent_file(tmp_path):
    nonexistent_file = tmp_path / 'nonexistent.txt'
    with pytest.raises(FileNotFoundError):
        SearchTermsLoader.load_terms(str(nonexistent_file))

def test_load_terms_from_unsupported_format(tmp_path):
    unsupported_file = tmp_path / 'terms.xyz'
    with open(unsupported_file, 'w') as f:
        f.write('term1\nterm2\nterm3')
    
    with pytest.raises(SearchTermsLoader.UnsupportedFormatError) as exc_info:
        SearchTermsLoader.load_terms(str(unsupported_file))
    assert "Unsupported file format: xyz" == str(exc_info.value)

def test_load_terms_from_invalid_json(tmp_path):
    invalid_json = tmp_path / 'terms.json'
    with open(invalid_json, 'w') as f:
        f.write('{"invalid": json}')
    
    with pytest.raises(SearchTermsLoader.InvalidFormatError) as exc_info:
        SearchTermsLoader.load_terms(str(invalid_json))
    assert "Invalid file format:" in str(exc_info.value)

def test_load_terms_from_invalid_yaml(tmp_path):
    invalid_yaml = tmp_path / 'terms.yml'
    with open(invalid_yaml, 'w') as f:
        f.write('invalid: yaml: : :')
    
    with pytest.raises(SearchTermsLoader.InvalidFormatError):
        SearchTermsLoader.load_terms(str(invalid_yaml))

def test_load_terms_empty_file(tmp_path):
    empty_file = tmp_path / 'terms.txt'
    empty_file.touch()
    
    loaded_terms = SearchTermsLoader.load_terms(str(empty_file))
    assert loaded_terms == []

def test_load_terms_with_whitespace(tmp_path):
    whitespace_file = tmp_path / 'terms.txt'
    with open(whitespace_file, 'w') as f:
        f.write('  term1  \n\nterm2\n  term3  \n\n')
    
    loaded_terms = SearchTermsLoader.load_terms(str(whitespace_file))
    assert loaded_terms == ['term1', 'term2', 'term3']