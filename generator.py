import yaml

class YamlSchemaError(Exception):
    pass

CREATE_TABLE = """
CREATE TABLE \"{table}\" (
    {table}_id serial PRIMARY KEY,
    {columns},
    {table}_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    {table}_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

"""
CREATE_TRIGGER = """
CREATE OR REPLACE FUNCTION {table}_insertFunc() RETURNS trigger AS \'BEGIN
    NEW.{table}_updated = now();
    RETURN NEW;
    END;\'
LANGUAGE 'plpgsql';

CREATE TRIGGER \"{table}_updateTrigger\" BEFORE UPDATE ON  \"{table}\"
FOR EACH ROW EXECUTE PROCEDURE {table}_insertFunc();

"""
CREATE_ALTER_ID = """ALTER TABLE "{child}" ADD "{parent}_id" INTEGER NOT NULL;"""
CREATE_ALTER_FK = """
ALTER TABLE "{child}"
    ADD CONSTRAINT fk_{child}_{parent}
    FOREIGN KEY ({parent}_id)
    REFERENCES "{parent}" ({parent}_id);
"""
CREATE_BINDING_TABLE = """
CREATE TABLE "{table1}_{table2}" (
    {table1}_id INTEGER,
    {table2}_id INTEGER,
    PRIMARY KEY ({table1}_id, {table2}_id)
);

"""

class Generator(object):
    
    def __init__(self):
        self._alters   = set()
        self._tables   = set()
        self._triggers = set()

    def __build_tables(self):
        for table in self.__schema:
            self._tables.add(CREATE_TABLE.format(columns=self.__build_columns(table), table=table.lower()))
        

    def __build_columns(self, entity):
        return ',\n    '.join("{0}_{1} {2}".format(entity.lower(), field, key) for field, key in self.__schema[entity]['fields'].items())

    def __build_relations(self):
        for entity, structure in self.__schema.items():
            for other_entity, relation in structure['relations'].items():
                reverse_relation = self.__schema[other_entity]['relations'][entity]
                if relation == 'one' and reverse_relation == 'many':
                    self.__build_many_to_one(entity, other_entity)
                elif relation == 'many' and  reverse_relation == 'many':
                    if entity < other_entity:
                        self.__build_many_to_many(entity, other_entity)
                elif relation != 'many' and reverse_relation != 'one':
                    raise YamlSchemaError('Error in ' + other_entity  + ' relation ' + reverse_relation + ', table ' + entity + ' ' + relation)


    def __build_many_to_one(self, child, parent):
        self._alters.add((CREATE_ALTER_ID + CREATE_ALTER_FK).format(child=child.lower(), parent=parent.lower()))

    def __build_many_to_many(self, left, right):
        left  = left.lower()
        right = right.lower()
        table_name = left + '__' + right

        self._tables.add(CREATE_BINDING_TABLE.format(table1=left, table2=right))
        self._alters.add(CREATE_ALTER_FK.format(child=table_name, parent=left))
        self._alters.add(CREATE_ALTER_FK.format(child=table_name, parent=right))

    def __build_triggers(self):
        for table_name in self.__schema:
            self._triggers.add(CREATE_TRIGGER.format(table=table_name.lower()))

    def build_ddl(self, filename):
        #fill tables, alters and triggers
        file = open(filename, 'r')
        self.__schema = yaml.load(file)

        self.__build_tables()
        self.__build_relations()
        self.__build_triggers()

    def clear(self):
        self._alters.clear()
        self._tables.clear()
        self._triggers.clear()
        self.__schema = ''

    def dump(self, filename):
        with open(filename, 'w') as file:
            file.write('\n'.join(table for table in self._tables))
            file.write('\n'.join(alter for alter in self._alters))
            file.write('\n'.join(trigger for trigger in self._triggers))

    
if __name__ == "__main__":
    ddl = Generator()
    ddl.build_ddl("Structure.yaml")
    ddl.dump('output.sql')

